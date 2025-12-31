from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.article_repo import ArticleRepository
from app.services.mistral_service import MistralService
from app.services.tagging_service import TaggingService
from app.services.search_service import SearchService

async def get_article_repo(session: AsyncSession = Depends(get_db)) -> ArticleRepository:
    return ArticleRepository(session)

def get_mistral_service() -> MistralService:
    return MistralService()

async def get_tagging_service(
        article_repo: ArticleRepository = Depends(get_article_repo),
        mistral_service: MistralService = Depends(get_mistral_service)
) -> TaggingService:
    return TaggingService(article_repo=article_repo, mistral_service=mistral_service)

async def get_search_service(
        article_repo: ArticleRepository = Depends(get_article_repo),
        mistral_service: MistralService = Depends(get_mistral_service)
) -> SearchService:
    return SearchService(article_repo=article_repo, mistral_service=mistral_service)

DBSessionDep = Annotated[AsyncSession, Depends(get_db)]
TaggingServiceDep = Annotated[TaggingService, Depends(get_tagging_service)]
SearchServiceDep = Annotated[SearchService, Depends(get_search_service)]