import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.search_service import SearchService
from app.schemas.ai import SearchAnalysisResult, UserIntentEnum
from app.models.article import Article


@pytest.fixture
def mock_repo():
    return AsyncMock()


@pytest.fixture
def mock_mistral():
    return AsyncMock()


@pytest.fixture
def search_service(mock_repo, mock_mistral):
    return SearchService(article_repo=mock_repo, mistral_service=mock_mistral)


@pytest.fixture
def mock_article():
    article = Article(
        id=101,
        title="Umgang mit Panik",
        content="Ein umfassender Inhalt über Panikattacken und deren Bewältigung im klinischen Kontext.",
        publication_date=None,
        ai_analysis={
            "summary": "Ein Ratgebertext über den Umgang mit Panikattacken.",
            "category": "Ratgeber",
            "sentiment": "neutral",
            "tags": ["Panik", "Angst", "Therapie", "Intervention", "Symptome",
                     "Behandlung", "Kognition", "Emotion", "Verhalten", "Diagnose",
                     "Prävention", "Forschung", "Methodik", "Evaluation", "Psychologie"]
        }
    )
    return article


@pytest.mark.asyncio
async def test_perform_search_standard_intent(
        search_service,
        mock_mistral,
        mock_repo,
        mock_article
):
    query = "Was tun bei Angst?"

    # SearchAnalysisResult requires 2-8 tags
    ai_result = SearchAnalysisResult(
        tags=["Angst", "Panik", "Symptome"],
        intent=UserIntentEnum.SELF_HELP,
        corrected_query="Was tun bei Angst?"
    )
    mock_mistral.analyze_search_query.return_value = ai_result

    mock_repo.search_by_overlap_coefficient.return_value = [(mock_article, 0.85)]

    result = await search_service.perform_search(query)

    assert result["metadata"]["detected_intent"] == UserIntentEnum.SELF_HELP
    assert result["metadata"]["is_emergency_context"] is False
    assert result["metadata"]["result_count"] == 1

    results_list = result["results"]
    assert results_list[0]["id"] == 101
    assert results_list[0]["relevance_score"] == 0.85
    assert results_list[0]["title"] == "Umgang mit Panik"

    mock_repo.search_by_overlap_coefficient.assert_called_once_with(
        query_tags=["Angst", "Panik", "Symptome"],
        threshold=0.3
    )


@pytest.mark.asyncio
async def test_perform_search_emergency_intent(
        search_service,
        mock_mistral,
        mock_repo
):
    query = "Ich will nicht mehr leben"

    # SearchAnalysisResult requires 2-8 tags
    ai_result = SearchAnalysisResult(
        tags=["Suizid", "Krise", "Hilfe"],
        intent=UserIntentEnum.EMERGENCY,
        corrected_query="Ich will nicht mehr leben"
    )
    mock_mistral.analyze_search_query.return_value = ai_result

    mock_repo.search_by_overlap_coefficient.return_value = []

    result = await search_service.perform_search(query)

    assert result["metadata"]["detected_intent"] == UserIntentEnum.EMERGENCY
    assert result["metadata"]["is_emergency_context"] is True

    mock_repo.search_by_overlap_coefficient.assert_called_once_with(
        query_tags=["Suizid", "Krise", "Hilfe"],
        threshold=0.2
    )


@pytest.mark.asyncio
async def test_perform_search_no_results(
        search_service,
        mock_mistral,
        mock_repo
):
    query = "Unbekanntes Thema"

    # SearchAnalysisResult requires 2-8 tags (minimum 2!)
    ai_result = SearchAnalysisResult(
        tags=["Unbekannt", "Sonstiges"],  # Fixed: now has 2 tags
        intent=UserIntentEnum.RESEARCH,
        corrected_query=None
    )
    mock_mistral.analyze_search_query.return_value = ai_result
    mock_repo.search_by_overlap_coefficient.return_value = []

    result = await search_service.perform_search(query)

    assert result["results"] == []
    assert result["metadata"]["result_count"] == 0