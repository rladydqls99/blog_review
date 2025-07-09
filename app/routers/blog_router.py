"""
블로그 리뷰 분석 API 라우터

이 모듈은 블로그 리뷰 분석 관련 API 엔드포인트를 정의합니다.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_blog_review_service
from app.services.blog_review_service import BlogReviewService

# 라우터 인스턴스 생성
router = APIRouter(
    prefix="/api/blog",
    tags=["블로그 리뷰 분석"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)


@router.get(
    "/search",
    response_model=str,
    summary="블로그 리뷰 분석",
    description="키워드로 블로그를 검색하고, 최신 포스트를 분석하여 리뷰를 요약합니다.",
)
async def search_blogs_and_analyze(
    service: Annotated[BlogReviewService, Depends(get_blog_review_service)],
    query: str = Query(
        ...,
        description="분석할 검색어 (예: '대전 맛집')",
        min_length=1,
        max_length=50,
        example="대전 공주칼국수",
    ),
) -> str:
    """
    블로그 검색, 크롤링, AI 분석을 수행하는 API 엔드포인트입니다.

    - 키워드를 받아 네이버 블로그를 검색합니다.
    - 검색된 블로그 중 최신 포스트 2개를 크롤링합니다.
    - 크롤링된 내용을 바탕으로 AI가 리뷰를 분석하고 요약합니다.

    Args:
        service: 주입된 BlogReviewService 인스턴스
        query: 검색 및 분석을 위한 키워드

    Returns:
        AI가 생성한 블로그 리뷰 분석 결과 (문자열)

    Raises:
        HTTPException: 처리 중 예상치 못한 오류 발생 시
    """
    try:
        # 서비스 레이어에 비즈니스 로직 처리를 위임합니다.
        result = await service.analyze_reviews(query=query)

        # 디버깅용 로그 (결과 확인 시 사용)
        # print("최종 AI 답변:", result)

        return result

    except HTTPException as e:
        # 서비스 레이어에서 발생한 HTTP 예외는 그대로 다시 발생시킵니다.
        raise e
    except Exception as e:
        # 그 외 예상치 못한 오류를 처리합니다.
        # 실제 운영 환경에서는 에러 로깅이 중요합니다.
        # logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
