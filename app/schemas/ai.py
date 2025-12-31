from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

class SentimentEnum(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    CONCERN = "concern"

class UserIntentEnum(str, Enum):
    RESEARCH = "research"
    SELF_HELP = "self_help"
    EMERGENCY = "emergency"
    GENERAL_INFO = "general_info"

class ArticleAnalysisResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tags: List[str] = Field(
        ...,
        min_length=15,
        max_length=40,
        description="Eine umfangreiche Liste von 15 bis 40 psychologischen Fachbegriffen, Synonymen und Themen, die den Text detailliert beschreiben."
    )

    scientific_disciplines: List[str] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Die wissenschaftlichen Teildisziplinen (z.B. Klinische Psychologie, Entwicklungspsychologie)."
    )

    summary: str = Field(
        ...,
        max_length=500,
        description="Eine detaillierte Zusammenfassung der Kerninhalte und Ergebnisse."
    )

    sentiment: SentimentEnum = Field(..., description="Die emotionale Grundstimmung.")

    category: str = Field(..., description="Art des Artikels (Studie, Review, etc.).")

    confidence_score: float = Field(..., ge=0.0, le=1.0)


class SearchAnalysisResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tags: List[str] = Field(
        ...,
        min_length=2,
        max_length=8,
        description="Eine präzise Auswahl von 2 bis 8 Suchbegriffen, die die Absicht des Nutzers am besten repräsentieren."
    )

    intent: UserIntentEnum = Field(
        ...,
        description="Die vermutete Absicht hinter der Suchanfrage."
    )

    corrected_query: Optional[str] = Field(
        None,
        description="Eine korrigierte Version der Suchanfrage, falls Tippfehler oder Unklarheiten vorlagen."
    )