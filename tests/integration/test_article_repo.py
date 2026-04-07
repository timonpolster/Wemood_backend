"""Integrationstests für das ArticleRepository (CRUD und Overlap-Suche)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.article_repo import ArticleRepository
from app.schemas.article import ArticleCreate
from app.schemas.ai import ArticleAnalysisResult, SentimentEnum


def generate_valid_tags(base_tags: list[str]) -> list[str]:
    """Erweitert Basis-Tags mit Füll-Tags um das Minimum von 20 Tags zu erreichen."""
    filler_tags = [
        "Psychologie", "Intervention", "Behandlung", "Diagnose", "Symptome",
        "Forschung", "Studie", "Analyse", "Methodik", "Evaluation",
        "Prävention", "Therapie", "Kognition", "Emotion", "Verhalten",
        "Resilienz", "Selbstwirksamkeit", "Persönlichkeit", "Entwicklung", "Stress"
    ]
    combined = list(set(base_tags + filler_tags))
    return combined[:max(20, len(combined))]


def generate_valid_content(topic: str) -> str:
    """Generiert Inhalt der das Minimum von 50 Wörtern erfüllt."""
    return f"This is a comprehensive psychological article about {topic}. " * 5


@pytest.fixture
def article_repo(db_session: AsyncSession):
    """Erzeugt ein ArticleRepository mit der Test-DB-Session."""
    return ArticleRepository(db_session)


@pytest.mark.asyncio
async def test_create_and_retrieve_article(article_repo: ArticleRepository):
    """Testet Artikel-Erstellung mit KI-Daten und anschließenden Abruf per ID."""
    article_in = ArticleCreate(
        title="Integration Test Article",
        content=generate_valid_content("integration testing"),
        sources=["Test DB"]
    )

    ai_data = ArticleAnalysisResult(
        tags=generate_valid_tags(["Integration", "Test", "Database"]),
        scientific_disciplines=["Informatik"],
        summary="A comprehensive summary of the integration test article for database operations.",
        sentiment=SentimentEnum.POSITIVE,
        category="Test Category",
        confidence_score=0.99
    )

    created = await article_repo.create_with_ai_analysis(article_in, ai_data)

    assert created.id is not None
    assert created.title == "Integration Test Article"
    assert len(created.ai_analysis["tags"]) >= 15

    fetched = await article_repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id


@pytest.mark.asyncio
async def test_search_overlap_logic(article_repo: ArticleRepository):
    """Testet dass die Overlap-Suche Artikel mit übereinstimmenden Tags findet."""
    article_in = ArticleCreate(
        title="Panic Attack Guide",
        content=generate_valid_content("panic attacks and anxiety management"),
        sources=["Test DB"]
    )

    # Create tags that include our search terms plus fillers to meet minimum
    base_tags = ["Angst", "Panik", "Therapie", "Hilfe", "Symptom"]
    full_tags = generate_valid_tags(base_tags)

    ai_data = ArticleAnalysisResult(
        tags=full_tags,
        scientific_disciplines=["Klinische Psychologie"],
        summary="A comprehensive guide about panic attacks and their management strategies.",
        sentiment=SentimentEnum.NEUTRAL,
        category="Ratgeber",
        confidence_score=0.95
    )

    await article_repo.create_with_ai_analysis(article_in, ai_data)

    # Search Query: 3 Tags, should find matches with "Angst" and "Panik"
    query_tags = ["Angst", "Panik", "Schlaf"]

    results = await article_repo.search_by_overlap_coefficient(
        query_tags=query_tags,
        threshold=0.3  # Lower threshold since we have more tags now
    )

    assert len(results) == 1
    article, score = results[0]
    assert article.title == "Panic Attack Guide"
    assert score > 0.3  # At least matches threshold


@pytest.mark.asyncio
async def test_search_no_overlap(article_repo: ArticleRepository):
    """Testet dass bei komplett unverwandten Tags keine Ergebnisse zurückkommen."""
    article_in = ArticleCreate(
        title="Depression Study",
        content=generate_valid_content("depression and mood disorders"),
        sources=["Test DB"]
    )

    ai_data = ArticleAnalysisResult(
        tags=generate_valid_tags(["Depression", "Traurigkeit", "Stimmung"]),
        scientific_disciplines=["Klinische Psychologie"],
        summary="A detailed study about depression and its various manifestations in clinical settings.",
        sentiment=SentimentEnum.NEGATIVE,
        category="Studie",
        confidence_score=0.9
    )
    await article_repo.create_with_ai_analysis(article_in, ai_data)

    # Search for completely unrelated tags
    query_tags = ["Freude", "Glück", "Optimismus"]

    results = await article_repo.search_by_overlap_coefficient(query_tags, threshold=0.1)

    assert len(results) == 0