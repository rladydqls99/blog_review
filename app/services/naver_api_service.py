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
    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = "https://openapi.naver.com/v1/search/blog.json"
        self.headers = {
            "X-Naver-Client-Id": self.settings.naver_client_id,
            "X-Naver-Client-Secret": self.settings.naver_client_secret,
            "User-Agent": "Blog-Review-App/1.0",
        }

    def _remove_html_tags(self, text: str) -> str:
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
