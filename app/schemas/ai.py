from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

class SentimentEnum(str, Enum):
    """Mögliche Sentiment-Werte eines analysierten Artikels."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    CONCERN = "concern"

class UserIntentEnum(str, Enum):
    """Klassifikation der Benutzerabsicht hinter einer Suchanfrage."""
    RESEARCH = "research"
    SELF_HELP = "self_help"
    EMERGENCY = "emergency"
    GENERAL_INFO = "general_info"

class ArticleAnalysisResult(BaseModel):
    """Schema für das strukturierte Ergebnis der KI-Artikelanalyse."""
    model_config = ConfigDict(from_attributes=True)

    tags: List[str] = Field(
        ...,
        min_length=20,
        max_length=50,
        description="Eine umfangreiche Liste von 20 bis 50 psychologischen Fachbegriffen, Synonymen, verwandten Begriffen und Themen, die den Text detailliert beschreiben."
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
    """Schema für das strukturierte Ergebnis der KI-Suchanfragenanalyse."""
    model_config = ConfigDict(from_attributes=True)

    tags: List[str] = Field(
        ...,
        min_length=8,
        max_length=15,
        description="Eine umfassende Auswahl von 8 bis 15 Suchbegriffen inkl. Synonymen, verwandten Begriffen und Ober-/Unterkategorien, um die Trefferquote zu maximieren."
    )

    intent: UserIntentEnum = Field(
        ...,
        description="Die vermutete Absicht hinter der Suchanfrage."
    )

    corrected_query: Optional[str] = Field(
        None,
        description="Eine korrigierte Version der Suchanfrage, falls Tippfehler oder Unklarheiten vorlagen."
    )