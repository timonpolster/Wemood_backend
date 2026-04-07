from typing import List, Optional, Tuple
from sqlalchemy import select, text, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleUpdate
from app.schemas.ai import ArticleAnalysisResult

from app.core.logging_config import get_logger

logger = get_logger("repositories.article")

class ArticleRepository:
    """Repository für CRUD-Operationen und Suchfunktionen auf der Articles-Tabelle."""

    def __init__(self, session: AsyncSession):
        """Initialisiert das Repository mit einer async Datenbank-Session."""
        self.session = session

    async def create_with_ai_analysis(
            self, article_in: ArticleCreate, ai_data: ArticleAnalysisResult
    ) -> Article:
        """Erstellt einen Artikel mit zugehöriger KI-Analyse und persistiert ihn."""
        db_obj = Article(
            title=article_in.title,
            content=article_in.content,
            sources=article_in.sources,
            url=article_in.url,
            publication_date=article_in.publication_date,
            literature=article_in.literature,
            fazit=article_in.fazit,
            videos=article_in.videos,
            ai_analysis=ai_data.model_dump(mode="json")
        )
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def get_by_id(self, article_id: int) -> Optional[Article]:
        """Gibt einen Artikel anhand seiner ID zurück oder None."""
        query = select(Article).where(Article.id == article_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
            self,
            skip: int = 0,
            limit: int = 100
    ) -> Tuple[List[Article], int]:
        """Gibt eine paginierte Artikelliste und die Gesamtanzahl zurück."""

        # Get total count
        count_query = select(func.count()).select_from(Article)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Get the articles
        query = (
            select(Article)
            .order_by(Article.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        articles = result.scalars().all()

        return list(articles), total

    async def update(
            self,
            article_id: int,
            article_update: ArticleUpdate
    ) -> Optional[Article]:
        """Aktualisiert die Metadaten eines Artikels. Gibt None zurück falls nicht gefunden."""
        article = await self.get_by_id(article_id)
        if not article:
            return None

        update_data = article_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(article, field, value)

        await self.session.commit()
        await self.session.refresh(article)
        return article

    async def delete(self, article_id: int) -> bool:
        """Löscht einen Artikel. Gibt True bei Erfolg, False falls nicht gefunden."""
        article = await self.get_by_id(article_id)
        if not article:
            return False

        await self.session.delete(article)
        await self.session.commit()
        return True

    async def hybrid_search(
            self,
            query_text: str,
            query_tags: List[str],
            limit: int = 20,
            fulltext_weight: float = 0.4,
            tag_weight: float = 0.6,
            min_score: float = 0.01
    ) -> List[Tuple[Article, float, dict]]:
        """Kombinierte Suche aus PostgreSQL-Volltext und semantischem Tag-Matching mit gewichteter Bewertung."""

        if not query_text and not query_tags:
            return []

        query_tags_normalized = list(set(tag.lower().strip() for tag in query_tags)) if query_tags else []
        query_len = len(query_tags_normalized) if query_tags_normalized else 1

        # search query build
        search_terms = query_text if query_text else ""

        sql = text("""
            WITH search_scores AS (
                SELECT
                    a.*,
                    COALESCE(
                        ts_rank_cd(
                            setweight(to_tsvector('german', COALESCE(a.title, '')), 'A') ||
                            setweight(to_tsvector('german', COALESCE(a.content, '')), 'B'),
                            plainto_tsquery('german', :search_text),
                            32 
                        ),
                        0.0
                    ) AS fulltext_score,
                    
                    CASE
                        WHEN jsonb_array_length(COALESCE(a.ai_analysis->'tags', '[]'::jsonb)) > 0 
                             AND :query_len > 0
                        THEN (
                            SELECT COUNT(*)::float
                            FROM jsonb_array_elements_text(a.ai_analysis->'tags') AS doc_tag
                            WHERE LOWER(doc_tag) = ANY(:query_tags)
                        ) / LEAST(:query_len, jsonb_array_length(a.ai_analysis->'tags'))::float
                        ELSE 0.0
                    END AS tag_score,
                    
                    CASE
                        WHEN jsonb_array_length(COALESCE(a.ai_analysis->'tags', '[]'::jsonb)) > 0
                             AND :query_len > 0
                        THEN (
                            SELECT COUNT(DISTINCT doc_tag)::float
                            FROM jsonb_array_elements_text(a.ai_analysis->'tags') AS doc_tag
                            WHERE EXISTS (
                                SELECT 1 
                                FROM unnest(CAST(:query_tags AS text[])) AS search_tag
                                WHERE LOWER(doc_tag) LIKE '%%' || search_tag || '%%'
                                   OR search_tag LIKE '%%' || LOWER(doc_tag) || '%%'
                            )
                        ) / LEAST(:query_len, jsonb_array_length(a.ai_analysis->'tags'))::float
                        ELSE 0.0
                    END AS partial_tag_score
                    
                FROM articles a
                WHERE a.ai_analysis IS NOT NULL
            )
            SELECT 
                *,
                (
                    fulltext_score * :fulltext_weight + 
                    GREATEST(tag_score, partial_tag_score * 0.7) * :tag_weight
                ) AS combined_score
            FROM search_scores
            WHERE (
                fulltext_score > 0 
                OR tag_score > 0 
                OR partial_tag_score > 0
            )
            ORDER BY combined_score DESC, fulltext_score DESC, tag_score DESC
            LIMIT :limit
        """)

        logger.debug(f"Hybrid search: text='{search_terms[:50]}...', tags={query_tags_normalized[:5]}...")

        result = await self.session.execute(
            sql,
            {
                "search_text": search_terms,
                "query_tags": query_tags_normalized,
                "query_len": query_len,
                "fulltext_weight": fulltext_weight,
                "tag_weight": tag_weight,
                "limit": limit
            }
        )

        articles_with_scores = []
        for row in result:
            combined_score = float(row.combined_score) if row.combined_score else 0.0

            if combined_score >= min_score:
                article = Article(
                    id=row.id,
                    title=row.title,
                    content=row.content,
                    sources=row.sources,
                    url=row.url,
                    publication_date=row.publication_date,
                    literature=row.literature,
                    fazit=row.fazit,
                    videos=row.videos,
                    ai_analysis=row.ai_analysis,
                    created_at=row.created_at,
                    updated_at=row.updated_at
                )

                score_breakdown = {
                    "fulltext_score": round(float(row.fulltext_score) if row.fulltext_score else 0.0, 4),
                    "tag_score": round(float(row.tag_score) if row.tag_score else 0.0, 4),
                    "partial_tag_score": round(float(row.partial_tag_score) if row.partial_tag_score else 0.0, 4),
                    "combined_score": round(combined_score, 4)
                }

                articles_with_scores.append((article, combined_score, score_breakdown))

        logger.info(f"Hybrid search found {len(articles_with_scores)} results")
        return articles_with_scores

    async def search_by_overlap_coefficient(
            self, query_tags: List[str], limit: int = 15, threshold: float = 0.05
    ) -> List[Tuple[Article, float]]:
        """Sucht Artikel anhand des Overlap-Koeffizienten zwischen Query-Tags und Artikel-Tags."""
        if not query_tags:
            return []

        query_tags_normalized = list(set(tag.lower().strip() for tag in query_tags))
        query_len = len(query_tags_normalized)

        sql = text("""
            SELECT
                a.*,
                CASE
                    WHEN LEAST(:query_len, jsonb_array_length(COALESCE(a.ai_analysis->'tags', '[]'::jsonb))) > 0
                    THEN (
                        SELECT COUNT(*)::float
                        FROM jsonb_array_elements_text(a.ai_analysis->'tags') AS doc_tag
                        WHERE LOWER(doc_tag) = ANY(:query_tags)
                    ) / LEAST(:query_len, jsonb_array_length(a.ai_analysis->'tags'))::float
                    ELSE 0.0
                END AS overlap_score
            FROM articles a
            WHERE a.ai_analysis->'tags' IS NOT NULL
              AND jsonb_array_length(COALESCE(a.ai_analysis->'tags', '[]'::jsonb)) > 0
            ORDER BY overlap_score DESC
            LIMIT :limit
        """)

        result = await self.session.execute(
            sql,
            {
                "query_tags": query_tags_normalized,
                "query_len": query_len,
                "limit": limit
            }
        )

        articles_with_scores = []
        for row in result:
            article = Article(
                id=row.id,
                title=row.title,
                content=row.content,
                sources=row.sources,
                url=row.url,
                publication_date=row.publication_date,
                literature=row.literature,
                fazit=row.fazit,
                videos=row.videos,
                ai_analysis=row.ai_analysis,
                created_at=row.created_at,
                updated_at=row.updated_at
            )
            score = row.overlap_score if row.overlap_score else 0.0
            if score >= threshold:
                articles_with_scores.append((article, score))

        return articles_with_scores