from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.api.api_v1 import api_router
from app.db.session import engine

from app.core.logging_config import setup_logging, get_logger

setup_logging(level="INFO" if settings.ENVIRONMENT == "prod" else "DEBUG")
logger = get_logger("main")

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting WeMood Backend...")
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    logger.info("Database connection established")

    yield

    logger.info("Shutting down WeMood Backend...")
    await engine.dispose()
    logger.info("Database connection closed")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for WeMood - AI powered psychological search engine using Overlap Coefficient and Mistral AI.",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

if settings.ENVIRONMENT == "dev":
    allow_origins = ["*"]
else:
    allow_origins = [
        "https://wemood.at",
        "https://www.wemood.at"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "active",
        "environment": settings.ENVIRONMENT,
        "service": settings.PROJECT_NAME
    }