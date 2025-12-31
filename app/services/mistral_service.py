import json
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.prompts import PromptTemplates
from app.schemas.ai import ArticleAnalysisResult, SearchAnalysisResult

class MistralService:
    def __init__(self):
        self.api_key = settings.MISTRAL_API_KEY
        self.base_url = "https://api.mistral.ai/v1/chat/completions"
        self.model = "mistral-large-latest"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError))
    )
    async def _analyze_generic(self, system_prompt: str, few_shots: list, user_content: str, response_model: type):
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(few_shots)
        messages.append({"role": "user", "content": user_content})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()

            data = response.json()
            raw_content = data["choices"][0]["message"]["content"]

            try:
                parsed_json = json.loads(raw_content)
                return response_model(**parsed_json)
            except (json.JSONDecodeError, ValueError) as e:
                raise ValueError(f"Failed to parse AI response: {e}")

    async def analyze_article(self, title: str, content: str) -> ArticleAnalysisResult:
        user_prompt = PromptTemplates.build_article_prompt(title, content)
        return await self._analyze_generic(
            system_prompt=PromptTemplates.ARTICLE_SYSTEM_PROMPT,
            few_shots=PromptTemplates.ARTICLE_FEW_SHOTS,
            user_content=user_prompt,
            response_model=ArticleAnalysisResult
        )

    async def analyze_search_query(self, query: str) -> SearchAnalysisResult:
        user_prompt = PromptTemplates.build_search_prompt(query)
        return await self._analyze_generic(
            system_prompt=PromptTemplates.SEARCH_SYSTEM_PROMPT,
            few_shots=PromptTemplates.SEARCH_FEW_SHOTS,
            user_content=user_prompt,
            response_model=SearchAnalysisResult
        )