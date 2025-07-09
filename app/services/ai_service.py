from pydantic_settings import BaseSettings
from openai import OpenAI
from typing import List

from app.models.naver_models import NaverBlogCrawledResponse
from app.utils.prompt_utils import generate_prompt
from app.utils.prompt_utils import system_prompt


class OpenAISettings(BaseSettings):
    """
    OpenAI API 관련 설정을 관리하는 클래스

    .env 파일에서 OpenAI API 키를 로드
    """

    OPEN_AI_API_KEY: str

    class Config:
        env_file = ".env"
        extra = "ignore"  # 정의되지 않은 추가 환경변수 무시


class OpenAIService:
    """
    OpenAI API를 사용하여 블로그 분석 결과를 생성하는 서비스

    주요 기능:
    - 크롤링된 블로그 데이터를 OpenAI API로 분석
    - GPT 모델을 통한 리뷰 요약 및 분석 결과 생성
    """

    def __init__(self):
        """
        OpenAI 서비스 초기화

        설정:
        - 모델: gpt-4o-mini (비용 효율적이면서 성능 좋은 모델)
        - API 키: 환경변수에서 로드
        """
        self.model = "gpt-4o-mini"
        self.settings = OpenAISettings()
        self.client = OpenAI(api_key=self.settings.OPEN_AI_API_KEY)

    def generate_response(self, crawled_data: List[NaverBlogCrawledResponse]) -> str:
        """
        크롤링된 블로그 데이터를 분석하여 리뷰 요약을 생성

        Args:
            crawled_data: 네이버 블로그에서 크롤링된 데이터 리스트

        Returns:
            str: OpenAI가 생성한 블로그 리뷰 분석 결과

        Raises:
            Exception: OpenAI API 호출 실패 시 예외 발생
        """
        try:
            # 프롬프트 생성 및 디버깅용 출력
            user_prompt = generate_prompt(crawled_data)

            # OpenAI API 호출
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt()},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,  # 창의성과 일관성의 균형
                max_tokens=2000,  # 응답 길이 제한
            )

            return completion.choices[0].message.content

        except Exception as e:
            print(f"OpenAI API 호출 중 오류 발생: {e}")
            return f"분석 중 오류가 발생했습니다: {str(e)}"
