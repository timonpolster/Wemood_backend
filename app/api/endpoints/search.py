from typing import List, Optional
from datetime import date
from pydantic import BaseModel
from fastapi import APIRouter, Query, status
from app.api.dependencies import SearchServiceDep

router = APIRouter()

class SearchResultItem(BaseModel):
    id: int
    title: str
    summary: str
    category: str
    sentiment: str
    publication_date: Optional[date] = None
    relevance_score: float
    tags: List[str]

class SearchMetadata(BaseModel):
    original_query: str
    corrected_query: Optional[str]
    detected_intent: str
    used_tags: List[str]
    is_emergency_context: bool
    result_count: int

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
    summary="Semantic Search with AI Analysis",
    description="""
                    Analyzes the user's search query using Mistral AI to extract intent and semantic tags.
                    Performs an overlap-coefficient search on the database.
                    Returns ranked articles and metadata about the query interpretation.

                    **Emergency Detection:**
                    If the query indicates a potential crisis (suicidal ideation, self-harm), 
                    the response will include `emergency_resources` with German crisis hotlines and online help.
                """
)
async def search_articles(
        search_service: SearchServiceDep,
        q: str = Query(..., min_length=3, description="The user's search query (e.g., 'Hilfe bei Panikattacken')")
) -> SearchResponseWrapper:
    return await search_service.perform_search(q)