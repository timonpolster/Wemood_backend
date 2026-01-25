"""
Mistral AI Service for WeMood Backend.

Implements structured outputs using JSON-Schema as specified in the feasibility study.
Uses Few-Shot Prompting and enforces output structure via Pydantic schemas.
"""
import json
import httpx
from typing import Type, TypeVar
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings
from app.core.prompts import PromptTemplates
from app.schemas.ai import ArticleAnalysisResult, SearchAnalysisResult

# Generic type for Pydantic models
T = TypeVar('T', bound=BaseModel)


class MistralService:
    """
    Service for AI-powered text analysis using Mistral AI.
    
    Implements:
    - Few-Shot Prompting for consistent output quality
    - Structured Outputs via JSON-Schema enforcement
    - Exponential backoff retry for resilience
    """
    
    def __init__(self):
        self.api_key = settings.MISTRAL_API_KEY
        self.base_url = "https://api.mistral.ai/v1/chat/completions"
        self.model = "mistral-large-latest"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _build_json_schema_format(self, response_model: Type[T], schema_name: str) -> dict:
        """
        Build the response_format object for Mistral's Structured Outputs.
        
        Uses Pydantic's model_json_schema() to generate the JSON schema,
        then wraps it in Mistral's expected format.
        """
        # Get JSON schema from Pydantic model
        schema = response_model.model_json_schema()
        
        # Mistral requires additionalProperties: false for strict mode
        if "additionalProperties" not in schema:
            schema["additionalProperties"] = False
        
        return {
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "strict": True,
                "schema": schema
            }
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError))
    )
    async def _analyze_generic(
        self, 
        system_prompt: str, 
        few_shots: list, 
        user_content: str, 
        response_model: Type[T],
        schema_name: str
    ) -> T:
        """
        Generic analysis method using Mistral API with Structured Outputs.
        
        Args:
            system_prompt: The system role instructions
            few_shots: List of example messages for Few-Shot learning
            user_content: The actual content to analyze
            response_model: Pydantic model class for response validation
            schema_name: Name identifier for the JSON schema
            
        Returns:
            Validated Pydantic model instance
        """
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(few_shots)
        messages.append({"role": "user", "content": user_content})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "response_format": self._build_json_schema_format(response_model, schema_name)
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()

            data = response.json()
            raw_content = data["choices"][0]["message"]["content"]

            try:
                parsed_json = json.loads(raw_content)
                return response_model.model_validate(parsed_json)
            except json.JSONDecodeError as e:
                raise ValueError(f"Mistral returned invalid JSON: {e}")
            except Exception as e:
                raise ValueError(f"Failed to validate AI response against schema: {e}")

    async def analyze_article(self, title: str, content: str) -> ArticleAnalysisResult:
        """
        Analyze a psychological article and extract semantic metadata.
        
        Uses Few-Shot prompting to guide the AI in extracting:
        - 15-40 semantic tags
        - Scientific disciplines
        - Summary, sentiment, category
        - Confidence score
        """
        user_prompt = PromptTemplates.build_article_prompt(title, content)
        return await self._analyze_generic(
            system_prompt=PromptTemplates.ARTICLE_SYSTEM_PROMPT,
            few_shots=PromptTemplates.ARTICLE_FEW_SHOTS,
            user_content=user_prompt,
            response_model=ArticleAnalysisResult,
            schema_name="article_analysis"
        )

    async def analyze_search_query(self, query: str) -> SearchAnalysisResult:
        """
        Analyze a user search query and extract intent and tags.
        
        Handles:
        - Typo correction
        - Intent detection (research, self_help, emergency)
        - Semantic tag extraction for database matching
        """
        user_prompt = PromptTemplates.build_search_prompt(query)
        return await self._analyze_generic(
            system_prompt=PromptTemplates.SEARCH_SYSTEM_PROMPT,
            few_shots=PromptTemplates.SEARCH_FEW_SHOTS,
            user_content=user_prompt,
            response_model=SearchAnalysisResult,
            schema_name="search_analysis"
        )