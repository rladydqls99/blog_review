"""
블로그 검색 API 라우터

이 모듈은 네이버 블로그 검색 관련 API 엔드포인트를 정의합니다.
클라이언트가 블로그 검색을 요청할 수 있는 REST API를 제공합니다.
"""

from fastapi import APIRouter, HTTPException, Query

from app.services.naver_service import NaverBlogService
from app.models.naver_models import (
    NaverBlogSearchResponse,
    BlogSearchRequest,
)

# 라우터 인스턴스 생성
router = APIRouter(
    prefix="/api/blog",
    tags=["블로그 검색"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)

# 네이버 블로그 서비스 인스턴스
naver_service = NaverBlogService()


@router.get(
    "/search",
    response_model=NaverBlogSearchResponse,
    summary="블로그 검색",
    description="네이버 블로그 검색 API를 사용하여 블로그 포스트를 검색합니다.",
)
async def search_blogs(
    query: str = Query(
        ..., description="검색어", min_length=1, max_length=255, example="리뷰"
    ),
    display: int = Query(
        default=10,
        description="한 번에 표시할 검색 결과 개수 (1~100)",
        ge=1,
        le=100,
        example=10,
    ),
    start: int = Query(
        default=1, description="검색 시작 위치 (1~1000)", ge=1, le=1000, example=1
    ),
    sort: str = Query(
        default="sim",
        description="정렬 옵션 (sim: 정확도순, date: 날짜순)",
        regex="^(sim|date)$",
        example="sim",
    ),
) -> NaverBlogSearchResponse:
    """
    네이버 블로그 검색을 수행하는 API 엔드포인트

    이 엔드포인트는 다음과 같은 기능을 제공합니다:
    - 네이버 블로그 검색 API 호출
    - 검색 결과 파싱 및 정제
    - 구조화된 JSON 응답 반환

    Args:
        query: 검색할 키워드
        display: 한 번에 표시할 결과 개수 (기본값: 10)
        start: 검색 시작 위치 (기본값: 1)
        sort: 정렬 방식 (기본값: sim)

    Returns:
        블로그 검색 결과 (제목, 링크, 설명, 블로그명 등)

    Raises:
        HTTPException: API 호출 실패 또는 잘못된 파라미터
    """
    try:
        # 요청 파라미터 검증
        search_request = BlogSearchRequest(
            query=query,
            display=display,
            start=start,
            sort=sort,
        )

        # 네이버 API 호출
        result = await naver_service.search_blogs(search_request)

        return result

    except ValueError as e:
        # 파라미터 검증 실패
        raise HTTPException(status_code=400, detail=f"Invalid parameters: {str(e)}")
    except Exception as e:
        # 예상치 못한 오류
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
