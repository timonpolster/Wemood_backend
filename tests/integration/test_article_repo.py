import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.article_repo import ArticleRepository
from app.schemas.article import ArticleCreate
from app.schemas.ai import ArticleAnalysisResult, SentimentEnum

@pytest.fixture
def article_repo(db_session: AsyncSession):
    return ArticleRepository(db_session)

@pytest.mark.asyncio
async def test_create_and_retrieve_article(article_repo: ArticleRepository):
    article_in = ArticleCreate(
        title="Integration Test Article",
        content="This is content for the integration test.",
        source="Test DB"
    )

    ai_data = ArticleAnalysisResult(
        tags=["Tag1", "Tag2"],
        scientific_disciplines=["Discipline1"],
        summary="Summary",
        sentiment=SentimentEnum.POSITIVE,
        category="Test Category",
        confidence_score=0.99
    )

    created = await article_repo.create_with_ai_analysis(article_in, ai_data)

    assert created.id is not None
    assert created.title == "Integration Test Article"
    assert created.ai_analysis["tags"] == ["Tag1", "Tag2"]

    fetched = await article_repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id

@pytest.mark.asyncio
async def test_search_overlap_logic(article_repo: ArticleRepository):
    article_in = ArticleCreate(
        title="Panic Attack Guide",
        content="Deep content regarding panic...",
        source="Test Source"
    )

    # 5 Tags
    tags_in_db = ["Angst", "Panik", "Therapie", "Hilfe", "Symptom"]

    ai_data = ArticleAnalysisResult(
        tags=tags_in_db,
        scientific_disciplines=["Klinische Psychologie"],
        summary="Panic summary",
        sentiment=SentimentEnum.NEUTRAL,
        category="Ratgeber",
        confidence_score=0.95
    )

    await article_repo.create_with_ai_analysis(article_in, ai_data)

    # Search Query: 3 Tags, 2 Matches ("Angst", "Panik")
    # Overlap Calculation:
    # Intersection = 2
    # Min(|A|, |B|) = Min(5, 3) = 3
    # Expected Score = 2/3 approx 0.666

    query_tags = ["Angst", "Panik", "Schlaf"]

    results = await article_repo.search_by_overlap_coefficient(
        query_tags=query_tags,
        threshold=0.5
    )

    assert len(results) == 1

    article, score = results[0]

    assert article.title == "Panic Attack Guide"
    assert 0.66 < score < 0.67

@pytest.mark.asyncio
async def test_search_no_overlap(article_repo: ArticleRepository):
    article_in = ArticleCreate(title="Depression Study", content="...", source="Test")
    ai_data = ArticleAnalysisResult(
        tags=["Depression", "Traurigkeit"],
        scientific_disciplines=["Klinische Psychologie"],
        summary="...",
        sentiment=SentimentEnum.NEGATIVE,
        category="Studie",
        confidence_score=0.9
    )
    await article_repo.create_with_ai_analysis(article_in, ai_data)

    query_tags = ["Freude", "Glück"] # No match

    results = await article_repo.search_by_overlap_coefficient(query_tags, threshold=0.1)

    assert len(results) == 0