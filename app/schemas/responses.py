from datetime import datetime
from typing import Optional
from pydantic import ConfigDict, Field
from app.schemas.article import ArticleCreate
from app.schemas.ai import ArticleAnalysisResult

class ArticleResponse(ArticleCreate):
    """Antwortschema für einen Artikel inkl. ID, KI-Analyse und Zeitstempel."""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Die eindeutige ID des Artikels in der Datenbank.")

    ai_analysis: Optional[ArticleAnalysisResult] = Field(
        None,
        description="Die von der KI generierten Metadaten (Tags, Zusammenfassung, Sentiment)."
    )

    created_at: datetime = Field(..., description="Zeitstempel der Erstellung.")
    updated_at: datetime = Field(..., description="Zeitstempel der letzten Änderung.")