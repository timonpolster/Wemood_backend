"""Unit-Tests für den TaggingService (Pipeline, Validierung, Qualitätsprüfung)."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.services.tagging_service import TaggingService
from app.schemas.article import ArticleCreate
from app.schemas.ai import ArticleAnalysisResult, SentimentEnum
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
def tagging_service(mock_repo, mock_mistral):
    """Erzeugt einen TaggingService mit gemockten Abhängigkeiten."""
    return TaggingService(article_repo=mock_repo, mistral_service=mock_mistral)


@pytest.fixture
def valid_article_input():
    """Erzeugt einen validen ArticleCreate-Input für Tests."""
    return ArticleCreate(
        title="Valid Test Article",
        content="This is a sufficiently long text regarding psychology and mental health treatment. " * 10,
        sources=["Test Source"]
    )


@pytest.fixture
def valid_ai_result():
    """Erzeugt ein valides KI-Analyse-Ergebnis mit hoher Konfidenz."""
    return ArticleAnalysisResult(
        tags=[
            "Psychologie", "Test", "Analyse", "Forschung", "Methodik",
            "Klinische Psychologie", "Diagnose", "Behandlung", "Therapie", "Intervention",
            "Symptome", "Evaluation", "Prävention", "Verhalten", "Kognition",
            "Emotion", "Persönlichkeit", "Entwicklung", "Resilienz", "Selbstwirksamkeit"
        ],
        scientific_disciplines=["Klinische Psychologie"],
        summary="Eine valide Zusammenfassung des psychologischen Textes mit ausreichender Länge.",
        sentiment=SentimentEnum.NEUTRAL,
        category="Studie",
        confidence_score=0.95
    )


@pytest.mark.asyncio
async def test_process_article_pipeline_success(
        tagging_service,
        mock_mistral,
        mock_repo,
        valid_article_input,
        valid_ai_result
):
    """Testet die erfolgreiche Pipeline: Validierung, KI-Analyse und Persistierung."""
    mock_mistral.analyze_article.return_value = valid_ai_result

    mock_created_article = Article(id=1, title=valid_article_input.title)
    mock_repo.create_with_ai_analysis.return_value = mock_created_article

    result = await tagging_service.process_article_pipeline(valid_article_input)

    assert result.id == 1
    assert result.title == valid_article_input.title

    mock_mistral.analyze_article.assert_called_once_with(
        valid_article_input.title,
        valid_article_input.content
    )
    mock_repo.create_with_ai_analysis.assert_called_once_with(
        valid_article_input,
        valid_ai_result
    )


@pytest.mark.asyncio
async def test_process_article_pipeline_content_too_short(tagging_service):
    """Testet dass Artikel mit weniger als 50 Wörtern abgelehnt werden."""
    short_article = ArticleCreate(
        title="Short Content Article",
        content="This content is long enough in characters but has too few words for analysis purposes here.",
        sources=["Test"]
    )

    with pytest.raises(HTTPException) as exc_info:
        await tagging_service.process_article_pipeline(short_article)

    assert exc_info.value.status_code == 422
    assert "Minimum 50 words" in exc_info.value.detail


@pytest.mark.asyncio
async def test_process_article_pipeline_low_confidence(
        tagging_service,
        mock_mistral,
        mock_repo,
        valid_article_input,
        valid_ai_result
):
    """Testet dass ein KI-Ergebnis unter dem Konfidenz-Schwellenwert abgelehnt wird."""
    # Create a new AIResult with low confidence
    low_confidence_result = ArticleAnalysisResult(
        tags=valid_ai_result.tags,
        scientific_disciplines=valid_ai_result.scientific_disciplines,
        summary=valid_ai_result.summary,
        sentiment=valid_ai_result.sentiment,
        category=valid_ai_result.category,
        confidence_score=0.4  # Below threshold of 0.6
    )
    mock_mistral.analyze_article.return_value = low_confidence_result

    with pytest.raises(HTTPException) as exc_info:
        await tagging_service.process_article_pipeline(valid_article_input)

    assert exc_info.value.status_code == 422
    assert "Quality threshold" in exc_info.value.detail