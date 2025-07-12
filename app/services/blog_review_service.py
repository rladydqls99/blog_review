"""
블로그 리뷰 분석 비즈니스 로직을 총괄하는 서비스
"""

import logging
from typing import List

from app.models.naver_models import BlogSearchRequest, NaverBlogCrawledResponse
from app.services.ai_service import OpenAIService
from app.services.naver_api_service import NaverApiService
from crawler.naver_blog_crawler import NaverBlogCrawler

logger = logging.getLogger(__name__)


class BlogReviewService:
    def __init__(
        self,
        naver_api_service: NaverApiService,
        openai_service: OpenAIService,
    ):
        self.naver_api_service = naver_api_service
        self.openai_service = openai_service

    async def analyze_reviews(self, query: str) -> str:
        # 1. 네이버 API를 통해 블로그 검색
        search_request = BlogSearchRequest(query=query)
        search_result = await self.naver_api_service.search_blogs(search_request)

        # 2. 최신순으로 정렬 후, 지정된 개수만큼 선택
        sorted_items = sorted(
            search_result.items, key=lambda x: x.post_date, reverse=True
        )
        target_items = sorted_items

        # 3. 선택된 블로그 포스트 크롤링
        crawled_data_list: List[NaverBlogCrawledResponse] = []
        # 크롤러는 리소스를 사용하므로, 사용할 때마다 생성/종료합니다.
        with NaverBlogCrawler(headless=True) as crawler:
            for item in target_items:
                try:
                    crawled_data = crawler.get_blog_content(item.link)
                    if "error" not in crawled_data:
                        crawled_response = NaverBlogCrawledResponse(**crawled_data)
                        crawled_data_list.append(crawled_response)
                except Exception as e:
                    logger.error(f"블로그 크롤링 실패 ({item.link}): {str(e)}")
                    continue

        if not crawled_data_list:
            return "분석할 최신 블로그를 찾지 못했습니다. 다른 검색어로 시도해주세요."

        # 4. 크롤링된 데이터를 AI 서비스에 전달하여 분석 요청
        final_review = self.openai_service.generate_response(crawled_data_list)

        return final_review
