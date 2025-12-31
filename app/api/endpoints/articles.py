from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.article import ArticleCreate
from app.schemas.responses import ArticleResponse
from app.api.dependencies import TaggingServiceDep, get_article_repo
from app.repositories.article_repo import ArticleRepository

router = APIRouter()

@router.post(
    "/",
    response_model=ArticleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create and Analyze a new Article",
    description="Submits a new psychological article. Triggers the AI pipeline to generate tags, sentiment, and summary, then saves everything to the database."
)
async def create_article(
        article_in: ArticleCreate,
        tagging_service: TaggingServiceDep
) -> Any:
    return await tagging_service.process_article_pipeline(article_in)

@router.get(
    "/{article_id}",
    response_model=ArticleResponse,
    summary="Get Article by ID",
    description="Retrieves a specific article including its AI-generated analysis data."
)
async def read_article(
        article_id: int,
        repo: ArticleRepository = Depends(get_article_repo)
) -> Any:
    article = await repo.get_by_id(article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} not found"
        )
    return article