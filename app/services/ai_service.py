import logging
from openai import OpenAI
from typing import List

from app.core.config import Settings
from app.models.naver_models import NaverBlogCrawledResponse
from app.utils.prompt_utils import generate_prompt, system_prompt

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self, settings: Settings):
        self.model = "gpt-4o-mini"
        self.client = OpenAI(api_key=settings.open_ai_api_key)

    def generate_response(self, crawled_data: List[NaverBlogCrawledResponse]) -> str:
        try:
            user_prompt = generate_prompt(crawled_data)

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt()},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
            )

            return completion.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI API 호출 중 오류 발생: {e}")
            return "리뷰 분석 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
