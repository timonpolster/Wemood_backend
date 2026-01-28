from fastapi import APIRouter
from app.api.endpoints import articles, search, auth

api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    articles.router,
    prefix="/articles",
    tags=["Articles"]
)

api_router.include_router(
    search.router,
    prefix="/search",
    tags=["Search"]
)