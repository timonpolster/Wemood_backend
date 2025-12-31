from fastapi import HTTPException, status
from app.schemas.article import ArticleCreate
from app.schemas.ai import ArticleAnalysisResult
from app.models.article import Article
from app.repositories.article_repo import ArticleRepository
from app.services.mistral_service import MistralService

class TaggingService:
    def __init__(self, article_repo: ArticleRepository, mistral_service: MistralService):
        self.article_repo = article_repo
        self.mistral_service = mistral_service
        self.min_confidence_threshold = 0.60
        self.min_summary_length = 20

    async def process_article_pipeline(self, article_in: ArticleCreate) -> Article:
        self._validate_content_suitability(article_in.content)

        analysis_result = await self._perform_ai_analysis(article_in.title, article_in.content)

        self._enforce_quality_standards(analysis_result)

        created_article = await self.article_repo.create_with_ai_analysis(article_in, analysis_result)

        return created_article

    def _validate_content_suitability(self, content: str) -> None:
        word_count = len(content.split())
        if word_count < 50:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Content is too short for meaningful psychological analysis. Minimum 50 words required."
            )

    async def _perform_ai_analysis(self, title: str, content: str) -> ArticleAnalysisResult:
        try:
            return await self.mistral_service.analyze_article(title, content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"AI Analysis Service failed: {str(e)}"
            )

    def _enforce_quality_standards(self, result: ArticleAnalysisResult) -> None:
        if result.confidence_score < self.min_confidence_threshold:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"AI Confidence Score ({result.confidence_score}) is below the required quality threshold of {self.min_confidence_threshold}. Manual review required."
            )

        if len(result.summary) < self.min_summary_length:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="AI generated summary is too short/superficial. Re-processing might be needed."
            )