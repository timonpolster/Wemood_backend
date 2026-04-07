from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class ArticleCreate(BaseModel):
    """Eingabeschema zum Erstellen eines neuen Artikels."""
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(..., min_length=5, max_length=255)
    content: str = Field(..., min_length=50)
    sources: Optional[List[str]] = Field(
        default=None,
        description="Liste der Quellen des Artikels."
    )
    url: Optional[str] = Field(None)
    publication_date: Optional[date] = Field(None)
    literature: Optional[str] = Field(
        default=None,
        description="Weiterführende Literatur zum Artikel."
    )
    fazit: Optional[str] = Field(
        default=None,
        description="Fazit bzw. Schlussfolgerung des Artikels."
    )
    videos: Optional[str] = Field(
        default=None,
        description="Zugehörige Video-Links (z.B. YouTube-URLs)."
    )


class ArticleUpdate(BaseModel):
    """Eingabeschema zum Aktualisieren von Artikel-Metadaten. Alle Felder optional."""
    model_config = ConfigDict(from_attributes=True)

    title: Optional[str] = Field(None, min_length=5, max_length=255)
    sources: Optional[List[str]] = Field(
        default=None,
        description="Liste der Quellen des Artikels."
    )
    url: Optional[str] = Field(None)
    publication_date: Optional[date] = Field(None)
    literature: Optional[str] = Field(
        default=None,
        description="Weiterführende Literatur zum Artikel."
    )
    fazit: Optional[str] = Field(
        default=None,
        description="Fazit bzw. Schlussfolgerung des Artikels."
    )
    videos: Optional[str] = Field(
        default=None,
        description="Zugehörige Video-Links (z.B. YouTube-URLs)."
    )