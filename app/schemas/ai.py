from typing import List
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

class SentimentEnum(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    CONCERN = "concern"

class AIAnalysisResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tags: List[str] = Field(
        ...,
        min_length=3,
        max_length=10,
        description="Eine Liste von 3 bis 10 präzisen, psychologischen Fachbegriffen oder Schlüsselwörtern, die den Inhalt des Textes am besten beschreiben. Diese Tags werden für das Matching verwendet."
    )

    summary: str = Field(
        ...,
        max_length=400,
        description="Eine prägnante Zusammenfassung des Artikels in maximal zwei Sätzen. Dient als Vorschau für das Suchergebnis."
    )

    sentiment: SentimentEnum = Field(
        ...,
        description="Die emotionale Grundstimmung des Textes. 'concern' sollte gewählt werden, wenn akute psychische Belastung oder Gefahrenpotenzial erkannt wird."
    )

    category: str = Field(
        ...,
        description="Die primäre Kategorie des Textes, z.B. 'Klinische Studie', 'Ratgeber', 'Fallbericht', 'Therapieverfahren'."
    )

    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Ein Wert zwischen 0.0 und 1.0, der angibt, wie sicher sich das Modell bei der Analyse und den gewählten Tags ist."
    )