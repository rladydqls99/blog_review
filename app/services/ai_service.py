from openai import OpenAI
from typing import List

from app.core.config import Settings
from app.models.naver_models import NaverBlogCrawledResponse
from app.utils.prompt_utils import generate_prompt, system_prompt


class OpenAIService:
    """
    OpenAI API를 사용하여 블로그 분석 결과를 생성하는 서비스
    """

    def __init__(self, settings: Settings):
        """
        OpenAI 서비스 초기화

        Args:
            settings: 주입된 통합 설정 객체
        """
        self.model = "gpt-4o-mini"
        self.client = OpenAI(api_key=settings.open_ai_api_key)

    def generate_response(self, crawled_data: List[NaverBlogCrawledResponse]) -> str:
        """
        크롤링된 블로그 데이터를 분석하여 리뷰 요약을 생성합니다.

        Args:
            crawled_data: 네이버 블로그에서 크롤링된 데이터 리스트

        Returns:
            OpenAI가 생성한 블로그 리뷰 분석 결과
        """
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
            # 실제 운영 환경에서는 logger 사용을 권장합니다.
            print(f"OpenAI API 호출 중 오류 발생: {e}")
            # 사용자에게 직접적인 에러 메시지 노출은 최소화하는 것이 좋습니다.
            return "리뷰 분석 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
