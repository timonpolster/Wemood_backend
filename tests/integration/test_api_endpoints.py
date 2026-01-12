import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock

from app.main import app
from app.api.dependencies import get_mistral_service
from app.schemas.ai import ArticleAnalysisResult, SearchAnalysisResult, SentimentEnum, UserIntentEnum
from app.core.config import settings

@pytest.fixture
def mock_mistral_service():
    mock = AsyncMock()

    article_result = ArticleAnalysisResult(
        tags=["Integration", "Test", "System", "Database", "API"] * 4,
        scientific_disciplines=["Informatik"],
        summary="Integration Test Summary",
        sentiment=SentimentEnum.POSITIVE,
        category="Test Data",
        confidence_score=0.99
    )
    mock.analyze_article.return_value = article_result

    search_result = SearchAnalysisResult(
        tags=["Test", "Suche"],
        intent=UserIntentEnum.RESEARCH,
        corrected_query="Test Suche"
    )
    mock.analyze_search_query.return_value = search_result

    return mock

@pytest.mark.asyncio
async def test_create_article_flow(client: AsyncClient, mock_mistral_service):
    app.dependency_overrides[get_mistral_service] = lambda: mock_mistral_service

    payload = {
        "title": "Integration Test Article",
        "content": "Dies ist ein sehr langer Text der unbedingt für den Integrationstest verwendet werden muss " * 10,
        "source": "Pytest",
        "url": "http://localhost/test",
        "publication_date": "2024-01-01T12:00:00"
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
    payload = {
        "title": "Short",
        "content": "Too short",
        "source": "Pytest",
        "url": "http://localhost/fail"
    }

    response = await client.post(f"{settings.API_V1_STR}/articles/", json=payload)

    assert response.status_code == 422
    assert "Minimum 50 words" in response.json()["detail"]

@pytest.mark.asyncio
async def test_search_endpoint(client: AsyncClient, mock_mistral_service):
    app.dependency_overrides[get_mistral_service] = lambda: mock_mistral_service

    response = await client.get(f"{settings.API_V1_STR}/search/?q=Testanfrage")

    assert response.status_code == 200
    data = response.json()
    assert "metadata" in data
    assert "results" in data
    assert data["metadata"]["original_query"] == "Testanfrage"
    assert data["metadata"]["detected_intent"] == "research"

    app.dependency_overrides.clear()