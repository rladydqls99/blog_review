"""
블로그 검색 API 라우터

이 모듈은 네이버 블로그 검색 관련 API 엔드포인트를 정의합니다.
클라이언트가 블로그 검색을 요청할 수 있는 REST API를 제공합니다.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List

from app.services.naver_service import NaverBlogService
from app.models.naver_models import (
    BlogSearchRequest,
    NaverBlogCrawledResponse,
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
    response_model=List[NaverBlogCrawledResponse],
    summary="블로그 검색",
    description="네이버 블로그 검색 API를 사용하여 블로그 포스트를 검색합니다.",
)
async def search_blogs(
    query: str = Query(
        ...,  # 이것은 "필수 파라미터"를 의미 (없으면 422 에러 발생)
        description="검색어",
        min_length=1,
        max_length=50,
        example="대전 공주칼국수",
    ),
) -> List[NaverBlogCrawledResponse]:
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
        크롤링된 블로그 포스트 목록 (제목, 작성자, 날짜, 주소, 내용 등)

    Raises:
        HTTPException: API 호출 실패 또는 잘못된 파라미터
    """
    try:
        # 요청 파라미터 검증
        search_request = BlogSearchRequest(query=query)

        # 네이버 API 호출
        result = await naver_service.search_and_crawl_blogs(search_request)
        print(result, "result")

        return result

    except ValueError as e:
        # 파라미터 검증 실패
        raise HTTPException(status_code=400, detail=f"Invalid parameters: {str(e)}")
    except Exception as e:
        # 예상치 못한 오류
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
