"""
네이버 블로그 검색 API 응답 모델

이 모듈은 네이버 블로그 검색 API의 응답 데이터를 정의합니다.
XML 응답을 파싱하여 구조화된 데이터로 변환하기 위한 모델들입니다.
"""

from pydantic import BaseModel, Field
from typing import List


class BlogItem(BaseModel):
    """
    개별 블로그 포스트 정보를 나타내는 모델

    네이버 블로그 검색 결과의 각 항목을 표현합니다.
    HTML 태그가 포함된 제목과 설명을 정리된 텍스트로 변환합니다.
    """

    title: str = Field(..., description="블로그 포스트 제목 (HTML 태그 제거됨)")
    link: str = Field(..., description="블로그 포스트 URL")
    description: str = Field(..., description="블로그 포스트 요약 (HTML 태그 제거됨)")
    blog_name: str = Field(..., description="블로그 이름")
    blog_link: str = Field(..., description="블로그 메인 URL")
    post_date: str = Field(..., description="포스트 작성일 (YYYYMMDD 형식)")


class NaverBlogSearchResponse(BaseModel):
    """
    네이버 블로그 검색 API의 전체 응답을 나타내는 모델

    검색 결과의 메타데이터와 실제 블로그 포스트 목록을 포함합니다.
    """

    last_build_date: str = Field(..., description="검색 결과를 생성한 시간")
    total: int = Field(..., description="검색 결과 문서의 총 개수")
    start: int = Field(..., description="검색 시작 위치")
    display: int = Field(..., description="한 번에 표시할 검색 결과 개수")
    items: List[BlogItem] = Field(
        default_factory=list, description="블로그 포스트 목록"
    )


class NaverBlogCrawledResponse(BaseModel):
    """
    네이버 블로그 크롤링 결과를 나타내는 모델
    """

    title: str = Field(..., description="블로그 포스트 제목")
    author: str = Field(..., description="블로그 포스트 작성자")
    date: str = Field(..., description="블로그 포스트 작성일")
    address: str = Field(..., description="식당 주소")
    content: str = Field(..., description="식당 소개")
    url: str = Field(..., description="블로그 포스트 URL")
    iframe_used: bool = Field(..., description="iframe 사용 여부")


class BlogSearchRequest(BaseModel):
    """
    블로그 검색 요청 파라미터를 정의하는 모델

    네이버 API 호출 시 필요한 매개변수들을 검증합니다.
    """

    query: str = Field(..., min_length=1, max_length=255, description="검색어")
    display: int = Field(
        default=50, ge=1, le=100, description="한 번에 표시할 검색 결과 개수 (1~100)"
    )
    start: int = Field(default=1, ge=1, le=1000, description="검색 시작 위치 (1~1000)")
    sort: str = Field(
        default="sim",
        pattern="^(sim|date)$",
        description="정렬 옵션 (sim: 정확도순, date: 날짜순)",
    )
