from typing import List, Dict, Any, Tuple
from app.repositories.article_repo import ArticleRepository
from app.services.mistral_service import MistralService
from app.schemas.ai import SearchAnalysisResult, UserIntentEnum
from app.models.article import Article

from app.core.logging_config import get_logger

logger = get_logger("services.search")

EMERGENCY_RESOURCES = {
    "hotlines": [
        {
            "name": "Telefonseelsorge Österreich",
            "number": "142",
            "description": "Kostenlos, 24/7 erreichbar",
            "url": "https://www.telefonseelsorge.at"
        },
        {
            "name": "Rat auf Draht",
            "number": "147",
            "description": "Kostenlos, 24/7. für Kinder, Jugendliche und deren Bezugspersonen",
            "url": "https://www.rataufdraht.at"
        },
        {
            "name": "Psychiatrische Soforthilfe Wien",
            "number": "01 31330",
            "description": "24/7 erreichbar",
            "url": "https://www.psd-wien.at"
        }
    ],
    "online_help": [
        {
            "name": "Telefonseelsorge Online",
            "url": "https://onlineberatung.telefonseelsorge.at",
            "description": "Chat und Mail-Beratung"
        },
        {
            "name": "Bitte lebe!",
            "url": "https://www.bittelebe.at",
            "description": "Suizidprävention Österreich"
        },
        {
            "name": "Rat auf Draht Online",
            "url": "https://www.rataufdraht.at/online-beratung",
            "description": "Chat-Beratung für Jugendliche"
        }
    ],
    "message": "Wenn du dich in einer akuten Krise befindest, wende dich bitte an professionelle Hilfe. Du bist nicht allein."
}

class SearchService:
    def __init__(self, article_repo: ArticleRepository, mistral_service: MistralService):
        self.article_repo = article_repo
        self.mistral_service = mistral_service

    async def perform_search(self, user_query: str) -> Dict[str, Any]:
        logger.info(f"Search request: '{user_query[:50]}...'")

        ai_analysis = await self._analyze_query_intent(user_query)
        logger.debug(f"Intent detected: {ai_analysis.intent}, Tags: {ai_analysis.tags}")

        is_emergency = self._check_for_emergency_intent(ai_analysis.intent)
        if is_emergency:
            logger.warning(f"EMERGENCY INTENT detected for query: {user_query}")

        search_threshold = 0.05 if is_emergency else 0.1
        search_limit = 20 if is_emergency else 15

        search_results = await self.article_repo.search_by_overlap_coefficient(
            query_tags=ai_analysis.tags,
            threshold=search_threshold,
            limit=search_limit
        )
        logger.info(f"Found {len(search_results)} articles")

        formatted_results = self._format_search_response(search_results)

        response = {
            "metadata": {
                "original_query": user_query,
                "corrected_query": ai_analysis.corrected_query,
                "detected_intent": ai_analysis.intent,
                "used_tags": ai_analysis.tags,
                "is_emergency_context": is_emergency,
                "result_count": len(formatted_results)
            },
            "results": formatted_results
        }

        if is_emergency:
            response["emergency_resources"] = EMERGENCY_RESOURCES
            logger.info("Emergency resources added to response")

        return response

    async def _analyze_query_intent(self, query: str) -> SearchAnalysisResult:
        return await self.mistral_service.analyze_search_query(query)

    def _check_for_emergency_intent(self, intent: UserIntentEnum) -> bool:
        return intent == UserIntentEnum.EMERGENCY

    def _format_search_response(self, results: List[Tuple[Article, float]]) -> List[Dict[str, Any]]:
        formatted = []
        for article, score in results:
            article_data = {
                "id": article.id,
                "title": article.title,
                "summary": article.ai_analysis.get("summary", "No summary available"),
                "category": article.ai_analysis.get("category", "Unknown"),
                "sentiment": article.ai_analysis.get("sentiment", "neutral"),
                "publication_date": article.publication_date,
                "relevance_score": round(score, 2),
                "tags": article.ai_analysis.get("tags", [])
            }
            formatted.append(article_data)
        return formatted