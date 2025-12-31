from datetime import datetime, date
from typing import Optional, Any
from sqlalchemy import String, Text, Date, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class Article(Base):
    __tablename__ = "articles"

    __table_args__ = (
        Index("ix_articles_ai_analysis_gin", "ai_analysis", postgresql_using="gin"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    content: Mapped[str] = mapped_column(Text, nullable=False)

    source: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    publication_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    ai_analysis: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=True,
        server_default='{}'
    )

    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<Article(id={self.id}, title='{self.title}', source='{self.source}')>"