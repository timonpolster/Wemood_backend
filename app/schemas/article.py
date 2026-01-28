from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class ArticleCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(..., min_length=5, max_length=255)
    content: str = Field(..., min_length=50)
    source: Optional[str] = Field(None, max_length=255)
    url: Optional[str] = Field(None)
    publication_date: Optional[date] = Field(None)


class ArticleUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: Optional[str] = Field(None, min_length=5, max_length=255)
    source: Optional[str] = Field(None, max_length=255)
    url: Optional[str] = Field(None)
    publication_date: Optional[date] = Field(None)