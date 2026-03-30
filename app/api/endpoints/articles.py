"""
Article API Endpoints for WeMood Backend.
Provides CRUD operations for psychological articles with AI analysis.
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel

from app.schemas.article import ArticleCreate, ArticleUpdate
from app.schemas.responses import ArticleResponse
from app.api.dependencies import TaggingServiceDep, get_article_repo
from app.repositories.article_repo import ArticleRepository
from app.core.security import get_current_user
from app.core.logging_config import get_logger

logger = get_logger("api.articles")

router = APIRouter()


class ArticleListResponse(BaseModel):
    """Response model for paginated article list."""
    articles: List[ArticleResponse]
    total: int
    skip: int
    limit: int


# ============== PUBLIC ENDPOINTS ==============

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
    """Get a single article by ID. Public endpoint."""
    article = await repo.get_by_id(article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} not found"
        )
    return article


# ============== PROTECTED ENDPOINTS (JWT Required) ==============

@router.get(
    "/",
    response_model=ArticleListResponse,
    summary="List All Articles",
    description="Get all articles with pagination. Requires authentication."
)
async def list_articles(
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(100, ge=1, le=500, description="Max records to return"),
        repo: ArticleRepository = Depends(get_article_repo),
        current_user: str = Depends(get_current_user)
) -> ArticleListResponse:
    """Get all articles with pagination. Protected endpoint."""
    articles, total = await repo.get_all(skip=skip, limit=limit)
    logger.info(f"User {current_user} listed articles (skip={skip}, limit={limit}, total={total})")
    return ArticleListResponse(
        articles=articles,
        total=total,
        skip=skip,
        limit=limit
    )


@router.post(
    "/",
    response_model=ArticleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create and Analyze Article",
    description="Create a new article with automatic AI analysis. Requires authentication."
)
async def create_article(
        article_in: ArticleCreate,
        tagging_service: TaggingServiceDep,
        current_user: str = Depends(get_current_user)
) -> Any:
    """
    Create a new article with AI-powered analysis.
    
    The AI will automatically:
    - Generate 20-50 semantic tags
    - Classify scientific disciplines
    - Create a summary
    - Determine sentiment and category
    """
    logger.info(f"User {current_user} creating article: {article_in.title}")
    result = await tagging_service.process_article_pipeline(article_in)
    logger.info(f"Article created with ID: {result.id}")
    return result


@router.put(
    "/{article_id}",
    response_model=ArticleResponse,
    summary="Update Article Metadata",
    description="Update article metadata (title, source, url, publication_date). Content cannot be changed. Requires authentication."
)
async def update_article(
        article_id: int,
        article_update: ArticleUpdate,
        repo: ArticleRepository = Depends(get_article_repo),
        current_user: str = Depends(get_current_user)
) -> Any:
    """
    Update article metadata.
    
    Note: Content and AI analysis cannot be modified.
    To change content, delete and recreate the article.
    """
    article = await repo.update(article_id, article_update)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} not found"
        )
    logger.info(f"User {current_user} updated article ID: {article_id}")
    return article


@router.delete(
    "/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Article",
    description="Permanently delete an article. Requires authentication."
)
async def delete_article(
        article_id: int,
        repo: ArticleRepository = Depends(get_article_repo),
        current_user: str = Depends(get_current_user)
) -> None:
    """Delete an article permanently."""
    deleted = await repo.delete(article_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} not found"
        )
    logger.info(f"User {current_user} deleted article ID: {article_id}")
