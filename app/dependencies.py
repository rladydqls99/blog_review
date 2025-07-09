"""
의존성 주입(Dependency Injection) 설정 모듈

이 모듈은 FastAPI의 Depends 시스템을 사용하여 서비스, 설정(Settings) 등의
의존성을 관리하고 제공하는 역할을 합니다.
"""
from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.core.config import Settings
from app.services.ai_service import OpenAIService
from app.services.naver_api_service import NaverApiService
from app.services.blog_review_service import BlogReviewService


# @lru_cache를 사용하여 각 함수가 처음 호출될 때의 반환 값을 캐싱합니다.
# 이를 통해 애플리케이션 전체에서 단일 인스턴스(싱글톤)를 유지할 수 있습니다.


@lru_cache
def get_settings() -> Settings:
    """통합 설정 객체를 반환합니다."""
    return Settings()


@lru_cache
def get_openai_service(
    settings: Annotated[Settings, Depends(get_settings)]
) -> OpenAIService:
    """OpenAI 서비스 객체를 생성하여 반환합니다."""
    return OpenAIService(settings=settings)


@lru_cache
def get_naver_api_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> NaverApiService:
    """네이버 API 서비스 객체를 생성하여 반환합니다."""
    return NaverApiService(settings=settings)


@lru_cache
def get_blog_review_service(
    naver_api_service: Annotated[NaverApiService, Depends(get_naver_api_service)],
    openai_service: Annotated[OpenAIService, Depends(get_openai_service)],
) -> BlogReviewService:
    """블로그 리뷰 서비스(오케스트레이터) 객체를 생성하여 반환합니다."""
    return BlogReviewService(
        naver_api_service=naver_api_service,
        openai_service=openai_service,
    )
