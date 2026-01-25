from typing import List, Optional, Tuple
from sqlalchemy import select, func, text, desc, case, Float
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import cast
from sqlalchemy.dialects.postgresql import JSONB, ARRAY, TEXT

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

        query_tags_set = set(query_tags)
        query_len = len(query_tags_set)

        pre_filter = Article.ai_analysis["tags"].has_any(list(query_tags_set))

        tags_unnested = func.jsonb_array_elements_text(Article.ai_analysis["tags"]).alias("tag")

        intersection_count_subquery = (
            select(func.count())
            .select_from(tags_unnested)
            .where(tags_unnested.c.tag.in_(query_tags_set))
            .scalar_subquery()
        )

        doc_len_expr = func.jsonb_array_length(Article.ai_analysis["tags"])

        min_len_expr = func.least(query_len, doc_len_expr)

        overlap_score_expr = case(
            (min_len_expr > 0, cast(intersection_count_subquery, Float) / cast(min_len_expr, Float)),
            else_=0.0
        ).label("overlap_score")

        stmt = (
            select(Article, overlap_score_expr)
            .where(pre_filter)
            .order_by(desc(overlap_score_expr))
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        articles_with_scores = []

        for row in result:
            article = row[0]
            score = row[1]
            if score >= threshold:
                articles_with_scores.append((article, score))

        return articles_with_scores