from typing import List, Optional, Tuple
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.schemas.article import ArticleCreate
from app.schemas.ai import ArticleAnalysisResult

class ArticleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_with_ai_analysis(
            self, article_in: ArticleCreate, ai_data: ArticleAnalysisResult
    ) -> Article:
        db_obj = Article(
            title=article_in.title,
            content=article_in.content,
            source=article_in.source,
            url=article_in.url,
            publication_date=article_in.publication_date,
            ai_analysis=ai_data.model_dump(mode="json")
        )
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def get_by_id(self, article_id: int) -> Optional[Article]:
        query = select(Article).where(Article.id == article_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def search_by_overlap_coefficient(
            self, query_tags: List[str], limit: int = 10, threshold: float = 0.3
    ) -> List[Tuple[Article, float]]:
        if not query_tags:
            return []

        query_tags_list = list(set(query_tags))
        query_len = len(query_tags_list)

        sql = text("""
                   SELECT
                       a.*,
                       CASE
                           WHEN LEAST(:query_len, jsonb_array_length(a.ai_analysis->'tags')) > 0
                               THEN (
                                        SELECT COUNT(*)::float
                                        FROM jsonb_array_elements_text(a.ai_analysis->'tags') AS doc_tag
                                        WHERE doc_tag = ANY(:query_tags)
                                    ) / LEAST(:query_len, jsonb_array_length(a.ai_analysis->'tags'))::float
                    ELSE 0.0
                   END AS overlap_score
            FROM articles a
            WHERE a.ai_analysis->'tags' ?| :query_tags
            ORDER BY overlap_score DESC
            LIMIT :limit
                   """)

        result = await self.session.execute(
            sql,
            {
                "query_tags": query_tags_list,
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
                source=row.source,
                url=row.url,
                publication_date=row.publication_date,
                ai_analysis=row.ai_analysis,
                created_at=row.created_at,
                updated_at=row.updated_at
            )
            score = row.overlap_score
            if score >= threshold:
                articles_with_scores.append((article, score))

        return articles_with_scores