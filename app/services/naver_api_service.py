"""
네이버 검색 API 서비스

이 모듈은 네이버 Open API를 사용하여 블로그 검색을 수행하고
JSON 응답을 파싱하여 구조화된 데이터로 변환하는 기능을 제공합니다.
"""

import httpx
import re
import logging
from fastapi import HTTPException
from typing import Dict, Any

from app.core.config import Settings
from app.models.naver_models import (
    NaverBlogSearchResponse,
    BlogSearchRequest,
    BlogItem,
)

logger = logging.getLogger(__name__)


class NaverApiService:
    """
    네이버 검색 API를 호출하는 서비스 클래스입니다.
    오직 네이버 API 연동 및 결과 파싱 책임만 가집니다.
    """

    def __init__(self, settings: Settings):
        """
        서비스 초기화

        주입된 설정 객체를 사용합니다.
        """
        self.settings = settings
        self.base_url = "https://openapi.naver.com/v1/search/blog.json"
        self.headers = {
            "X-Naver-Client-Id": self.settings.naver_client_id,
            "X-Naver-Client-Secret": self.settings.naver_client_secret,
            "User-Agent": "Blog-Review-App/1.0",
        }

    def _remove_html_tags(self, text: str) -> str:
        """HTML 태그를 제거하는 헬퍼 메서드"""
        # HTML 태그 제거 정규식 패턴
        clean_text = re.sub(r"<[^>]+>", "", text)
        # HTML 엔티티 디코딩
        clean_text = clean_text.replace("&lt;", "<")
        clean_text = clean_text.replace("&gt;", ">")
        clean_text = clean_text.replace("&amp;", "&")
        clean_text = clean_text.replace("&quot;", '"')
        clean_text = clean_text.replace("&apos;", "'")

        return clean_text.strip()

    async def search_blogs(
        self, search_params: BlogSearchRequest
    ) -> NaverBlogSearchResponse:
        """
        네이버 블로그 검색을 수행하는 메인 메서드

        Args:
            search_params: 검색 파라미터 (쿼리 등)

        Returns:
            블로그 검색 결과

        Raises:
            HTTPException: API 호출 실패 시
        """
        params = {
            "query": search_params.query,
            "display": 100,  # 우선 100개를 최대로 가져옵니다.
            "start": 1,
            "sort": "sim",  # 정확도 순으로 정렬
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    headers=self.headers,
                    params=params,
                    timeout=10.0,
                )
                response.raise_for_status()  # 2xx 이외의 상태 코드에 대해 예외 발생

                json_data = response.json()
                return self._parse_response(json_data)

        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Naver API request timeout")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                detail = "Invalid Naver API credentials"
            elif e.response.status_code == 429:
                detail = "API rate limit exceeded"
            else:
                detail = f"Naver API error: {e.response.text}"
            raise HTTPException(status_code=e.response.status_code, detail=detail)
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Network error: {str(e)}")

    def _parse_response(self, json_data: Dict[str, Any]) -> NaverBlogSearchResponse:
        """네이버 API JSON 응답을 파싱하여 모델로 변환합니다."""
        blog_items = [
            BlogItem(
                title=self._remove_html_tags(item.get("title", "")),
                link=item.get("link", ""),
                description=self._remove_html_tags(item.get("description", "")),
                blog_name=self._remove_html_tags(item.get("bloggername", "")),
                blog_link=item.get("bloggerlink", ""),
                post_date=item.get("postdate", ""),
            )
            for item in json_data.get("items", [])
        ]

        return NaverBlogSearchResponse(
            last_build_date=json_data.get("lastBuildDate", ""),
            total=json_data.get("total", 0),
            start=json_data.get("start", 1),
            display=json_data.get("display", 10),
            items=blog_items,
        )
