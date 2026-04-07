"""Unit-Tests für den SearchService (Intent-Erkennung, Emergency-Handling, Ergebnisformatierung)."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.search_service import SearchService
from app.schemas.ai import SearchAnalysisResult, UserIntentEnum
from app.models.article import Article


@pytest.fixture
def mock_repo():
    """Erzeugt ein gemocktes ArticleRepository."""
    return AsyncMock()


@pytest.fixture
def mock_mistral():
    """Erzeugt einen gemockten MistralService."""
    return AsyncMock()


@pytest.fixture
def search_service(mock_repo, mock_mistral):
    """Erzeugt einen SearchService mit gemockten Abhängigkeiten."""
    return SearchService(article_repo=mock_repo, mistral_service=mock_mistral)


@pytest.fixture
def mock_article():
    """Erzeugt einen Test-Artikel mit KI-Analyse-Daten."""
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
    """Testet eine normale Self-Help-Suche mit einem Treffer."""
    query = "Was tun bei Angst?"

    ai_result = SearchAnalysisResult(
        tags=["Angst", "Panik", "Symptome", "Angststörung", "Panikattacke",
              "Selbsthilfe", "Therapie", "Angstbewältigung"],
        intent=UserIntentEnum.SELF_HELP,
        corrected_query="Was tun bei Angst?"
    )
    mock_mistral.analyze_search_query.return_value = ai_result

    mock_repo.hybrid_search.return_value = [(mock_article, 0.85, {
        "fulltext_score": 0.0, "tag_score": 0.85,
        "partial_tag_score": 0.0, "combined_score": 0.85
    })]

    result = await search_service.perform_search(query)

    assert result["metadata"]["detected_intent"] == UserIntentEnum.SELF_HELP
    assert result["metadata"]["is_emergency_context"] is False
    assert result["metadata"]["result_count"] == 1

    results_list = result["results"]
    assert results_list[0]["id"] == 101
    assert results_list[0]["relevance_score"] == 0.85
    assert results_list[0]["title"] == "Umgang mit Panik"

    mock_repo.hybrid_search.assert_called_once_with(
        query_text="Was tun bei Angst?",
        query_tags=["Angst", "Panik", "Symptome", "Angststörung", "Panikattacke",
                    "Selbsthilfe", "Therapie", "Angstbewältigung"],
        limit=20, fulltext_weight=0.4,
        tag_weight=0.6, min_score=0.01
    )


@pytest.mark.asyncio
async def test_perform_search_emergency_intent(
        search_service,
        mock_mistral,
        mock_repo
):
    """Testet dass bei Krisen-Intent die Emergency-Suchkonfiguration verwendet wird."""
    query = "Ich will nicht mehr leben"

    ai_result = SearchAnalysisResult(
        tags=["Suizid", "Suizidgedanken", "Krise", "Krisenintervention",
              "Hilfe", "Notfall", "Depression", "Suizidprävention"],
        intent=UserIntentEnum.EMERGENCY,
        corrected_query="Ich will nicht mehr leben"
    )
    mock_mistral.analyze_search_query.return_value = ai_result

    mock_repo.hybrid_search.return_value = []

    result = await search_service.perform_search(query)

    assert result["metadata"]["detected_intent"] == UserIntentEnum.EMERGENCY
    assert result["metadata"]["is_emergency_context"] is True

    mock_repo.hybrid_search.assert_called_once_with(
        query_text="Ich will nicht mehr leben",
        query_tags=["Suizid", "Suizidgedanken", "Krise", "Krisenintervention",
                    "Hilfe", "Notfall", "Depression", "Suizidprävention"],
        limit=25, fulltext_weight=0.5,
        tag_weight=0.5, min_score=0.005
    )


@pytest.mark.asyncio
async def test_perform_search_no_results(
        search_service,
        mock_mistral,
        mock_repo
):
    """Testet dass bei fehlenden Treffern eine leere Ergebnisliste zurückkommt."""
    query = "Unbekanntes Thema"

    ai_result = SearchAnalysisResult(
        tags=["Unbekannt", "Sonstiges", "Allgemein", "Information",
              "Recherche", "Thema", "Psychologie", "Forschung"],
        intent=UserIntentEnum.RESEARCH,
        corrected_query=None
    )
    mock_mistral.analyze_search_query.return_value = ai_result
    mock_repo.hybrid_search.return_value = []

    result = await search_service.perform_search(query)

    assert result["results"] == []
    assert result["metadata"]["result_count"] == 0