"""
네이버 블로그 검색 API 서비스

이 모듈은 네이버 Open API를 사용하여 블로그 검색을 수행
JSON 응답을 파싱하여 구조화된 데이터로 변환하는 기능을 제공
"""

import httpx
import re
import logging
from fastapi import HTTPException
from pydantic_settings import BaseSettings
from typing import Dict, Any, List

from app.models.naver_models import (
    NaverBlogSearchResponse,
    BlogSearchRequest,
    BlogItem,
    NaverBlogCrawledResponse,
)
from crawler.naver_blog_crawler import NaverBlogCrawler

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    환경변수 설정을 관리하는 클래스

    .env 파일에서 네이버 API 인증 정보를 자동으로 로드
    """

    naver_client_id: str
    naver_client_secret: str

    class Config:
        env_file = ".env"


class NaverBlogService:
    """
    네이버 블로그 검색 API를 호출하는 서비스 클래스

    이 클래스는 다음과 같은 기능을 제공
    1. 네이버 API 인증 헤더 설정
    2. HTTP 요청 수행
    3. JSON 응답 파싱
    4. HTML 태그 제거
    """

    def __init__(self):
        """
        서비스 초기화

        환경변수에서 네이버 API 인증 정보를 로드
        """
        self.settings = Settings()  # 환경변수에서 네이버 API 인증 정보를 로드
        self.base_url = "https://openapi.naver.com/v1/search/blog.json"

        # API 인증 헤더 설정
        self.headers = {
            "X-Naver-Client-Id": self.settings.naver_client_id,
            "X-Naver-Client-Secret": self.settings.naver_client_secret,
            "User-Agent": "Blog-Review-App/1.0",
        }

    def _remove_html_tags(self, text: str) -> str:
        """
        HTML 태그를 제거하는 헬퍼 메서드

        Args:
            text: HTML 태그가 포함된 텍스트

        Returns:
            HTML 태그가 제거된 순수 텍스트
        """
        # HTML 태그 제거 정규식 패턴
        clean_text = re.sub(r"<[^>]+>", "", text)
        # HTML 엔티티 디코딩
        clean_text = clean_text.replace("&lt;", "<")
        clean_text = clean_text.replace("&gt;", ">")
        clean_text = clean_text.replace("&amp;", "&")
        clean_text = clean_text.replace("&quot;", '"')
        clean_text = clean_text.replace("&apos;", "'")

        return clean_text.strip()

    async def search_and_crawl_blogs(
        self, search_params: BlogSearchRequest
    ) -> List[NaverBlogCrawledResponse]:
        """
        블로그 검색 후, url을 바탕으로 상세 내용을 추출하는 메서드

        Args:
            search_params: 검색 파라미터 (쿼리, 표시 개수, 시작 위치, 정렬)

        Returns:
            블로그 검색 결과

        Raises:
            HTTPException: API 호출 실패 시
        """

        search_result = await self.search_blogs(search_params)

        with NaverBlogCrawler(headless=True) as crawler:
            crawled_data_list = []
            for item in search_result.items:
                try:
                    # 각 블로그 링크를 크롤링
                    crawled_data = crawler.get_blog_content(item.link)

                    # 크롤링 결과를 item에 추가
                    if "error" not in crawled_data:
                        crawled_response = NaverBlogCrawledResponse(
                            title=crawled_data.get("title", ""),
                            author=crawled_data.get("author", ""),
                            date=crawled_data.get("date", ""),
                            address=crawled_data.get("address", ""),
                            content=crawled_data.get("content", ""),
                            url=crawled_data.get("url", ""),
                            iframe_used=crawled_data.get("iframe_used", False),
                        )
                        crawled_data_list.append(crawled_response)

                except Exception as e:
                    logger.error(f"블로그 크롤링 실패 ({item.link}): {str(e)}")
                    continue

        return crawled_data_list

    async def search_blogs(
        self, search_params: BlogSearchRequest
    ) -> NaverBlogSearchResponse:
        """
        네이버 블로그 검색을 수행하는 메인 메서드

        Args:
            search_params: 검색 파라미터 (쿼리, 표시 개수, 시작 위치, 정렬)

        Returns:
            블로그 검색 결과

        Raises:
            HTTPException: API 호출 실패 시
        """
        # 쿼리 파라미터 구성
        params = {
            "query": search_params.query,
            "display": 100,
            "start": 1,
            "sort": "sim",
        }

        try:
            # 비동기 HTTP 클라이언트로 API 호출
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0,  # 30초 타임아웃
                )

                # HTTP 상태 코드 확인
                if response.status_code == 401:
                    raise HTTPException(
                        status_code=401, detail="Invalid Naver API credentials"
                    )
                elif response.status_code == 429:
                    raise HTTPException(
                        status_code=429, detail="API rate limit exceeded"
                    )
                elif response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Naver API error: {response.text}",
                    )

                # JSON 응답 파싱
                json_data = response.json()

                # 응답 데이터를 모델로 변환
                result = self._parse_response(json_data)

                # 최신 날짜 순으로 정렬
                result.items.sort(key=lambda x: x.post_date, reverse=True)

                # 열 개 추출
                result.items = result.items[:2]

                return result

        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Naver API request timeout")
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Network error: {str(e)}")

    def _parse_response(self, json_data: Dict[str, Any]) -> NaverBlogSearchResponse:
        """
        네이버 API JSON 응답을 파싱하여 모델로 변환

        Args:
            json_data: 네이버 API로부터 받은 JSON 응답

        Returns:
            파싱된 블로그 검색 결과
        """
        # 블로그 항목들 파싱
        blog_items = []
        for item in json_data.get("items", []):
            blog_item = BlogItem(
                title=self._remove_html_tags(item.get("title", "")),
                link=item.get("link", ""),
                description=self._remove_html_tags(item.get("description", "")),
                blog_name=self._remove_html_tags(item.get("bloggername", "")),
                blog_link=item.get("bloggerlink", ""),
                post_date=item.get("postdate", ""),
            )
            blog_items.append(blog_item)

        # 전체 응답 모델 생성
        return NaverBlogSearchResponse(
            last_build_date=json_data.get("lastBuildDate", ""),
            total=json_data.get("total", 0),
            start=json_data.get("start", 1),
            display=json_data.get("display", 10),
            items=blog_items,
        )
