from typing import List, Optional
from datetime import date
from pydantic import BaseModel
from fastapi import APIRouter, Query, status
from app.api.dependencies import SearchServiceDep

router = APIRouter()

class ScoreBreakdown(BaseModel):
    """breakdown of the relevance score for testeing"""
    fulltext_score: float
    tag_score: float
    partial_tag_score: float
    combined_score: float

class SearchResultItem(BaseModel):
    id: int
    title: str
    summary: str
    category: str
    sentiment: str
    publication_date: Optional[date] = None
    relevance_score: float
    score_breakdown: Optional[ScoreBreakdown] = None
    tags: List[str]

class SearchMetadata(BaseModel):
    original_query: str
    corrected_query: Optional[str]
    detected_intent: str
    used_tags: List[str]
    is_emergency_context: bool
    result_count: int
    search_strategy: str = "hybrid"

class EmergencyHotline(BaseModel):
    name: str
    number: str
    description: str
    url: Optional[str] = None

class EmergencyOnlineHelp(BaseModel):
    name: str
    url: str
    description: str

class EmergencyResources(BaseModel):
    hotlines: List[EmergencyHotline]
    online_help: List[EmergencyOnlineHelp]
    message: str

class SearchResponseWrapper(BaseModel):
    metadata: SearchMetadata
    results: List[SearchResultItem]
    emergency_resources: Optional[EmergencyResources] = None

@router.get(
    "/",
    response_model=SearchResponseWrapper,
    status_code=status.HTTP_200_OK,
    summary="Hybrid Semantic Search with AI Analysis",
    description= "AI-powered hybrid search combining full-text and semantic tag matching. Includes emergency detection for Austrian crisis hotlines."
)
async def search_articles(
        search_service: SearchServiceDep,
        q: str = Query(..., min_length=3, description="The user's search query (e.g., 'Hilfe bei Panikattacken')")
) -> SearchResponseWrapper:
    return await search_service.perform_search(q)