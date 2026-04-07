"""Integrationstests für die API-Endpunkte (Articles, Search)."""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock

from app.main import app
from app.api.dependencies import get_mistral_service
from app.schemas.ai import ArticleAnalysisResult, SearchAnalysisResult, SentimentEnum, UserIntentEnum
from app.core.config import settings


@pytest.fixture
def mock_mistral_service():
    """Erzeugt einen gemockten MistralService mit vordefinierten Analyse-Ergebnissen."""
    mock = AsyncMock()

    article_result = ArticleAnalysisResult(
        tags=[
            "Integration", "Test", "System", "Database", "API",
            "Backend", "Psychologie", "Analyse", "Forschung", "Methodik",
            "Klinische Psychologie", "Diagnose", "Behandlung", "Therapie", "Intervention",
            "Evaluation", "Prävention", "Symptome", "Kognition", "Verhalten"
        ],
        scientific_disciplines=["Informatik"],
        summary="Integration Test Summary für das Backend-System und die API-Endpunkte.",
        sentiment=SentimentEnum.POSITIVE,
        category="Test Data",
        confidence_score=0.99
    )
    mock.analyze_article.return_value = article_result

    search_result = SearchAnalysisResult(
        tags=["Test", "Suche", "Recherche", "Psychologie",
              "Information", "Analyse", "Forschung", "Ergebnis"],
        intent=UserIntentEnum.RESEARCH,
        corrected_query="Test Suche"
    )
    mock.analyze_search_query.return_value = search_result

    return mock


@pytest.mark.asyncio
async def test_create_article_flow(client: AsyncClient, mock_mistral_service):
    """Testet den vollständigen Artikel-Erstellungsflow inkl. KI-Analyse und anschließendem Abruf."""
    app.dependency_overrides[get_mistral_service] = lambda: mock_mistral_service

    payload = {
        "title": "Integration Test Article",
        "content": "Dies ist ein sehr langer Text der unbedingt für den Integrationstest verwendet werden muss und viele Wörter enthalten sollte. " * 10,
        "sources": ["Pytest"],
        "url": "http://localhost/test",
        "publication_date": "2024-01-01"  # Date format, not datetime
    }

    response = await client.post(f"{settings.API_V1_STR}/articles/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert "id" in data
    assert "ai_analysis" in data
    assert data["ai_analysis"]["confidence_score"] == 0.99

    article_id = data["id"]
    get_response = await client.get(f"{settings.API_V1_STR}/articles/{article_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == article_id

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_article_validation_error(client: AsyncClient):
    """Testet dass Artikel mit zu wenig Wörtern vom Service abgelehnt werden (422)."""
    # Content has >= 50 characters (passes Pydantic) but < 50 words (fails Service)
    payload = {
        "title": "Short Content Article",
        "content": "This content is long enough in characters but has way too few words to pass the service validation check.",
        "sources": ["Pytest"],
        "url": "http://localhost/fail"
    }

    response = await client.post(f"{settings.API_V1_STR}/articles/", json=payload)

    assert response.status_code == 422
    assert "Minimum 50 words" in response.json()["detail"]


@pytest.mark.asyncio
async def test_search_endpoint(client: AsyncClient, mock_mistral_service):
    """Testet den Search-Endpoint auf korrekte Metadaten und Struktur."""
    app.dependency_overrides[get_mistral_service] = lambda: mock_mistral_service

    response = await client.get(f"{settings.API_V1_STR}/search/?q=Testanfrage")

    assert response.status_code == 200
    data = response.json()
    assert "metadata" in data
    assert "results" in data
    assert data["metadata"]["original_query"] == "Testanfrage"
    assert data["metadata"]["detected_intent"] == "research"

    app.dependency_overrides.clear()