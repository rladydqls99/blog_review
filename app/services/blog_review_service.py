"""
블로그 리뷰 분석 비즈니스 로직을 총괄하는 서비스
"""

import logging
import asyncio
import time
from typing import List
from concurrent.futures import ThreadPoolExecutor

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

    def _crawl_single_url(self, url: str) -> dict:
        try:
            with NaverBlogCrawler(headless=True) as crawler:
                return crawler.get_blog_content(url)
        except Exception as e:
            logger.error(f"블로그 크롤링 실패 ({url}): {str(e)}")
            return {"error": f"크롤링 실패: {str(e)}"}

    async def analyze_reviews(self, query: str) -> str:
        # 1. 네이버 API를 통해 블로그 검색
        search_request = BlogSearchRequest(query=query)
        search_result = await self.naver_api_service.search_blogs(search_request)

        # 2. 최신순으로 정렬 후, 지정된 개수만큼 선택
        sorted_items = sorted(
            search_result.items, key=lambda x: x.post_date, reverse=True
        )
        target_items = sorted_items

        # 3. 멀티스레딩을 사용한 병렬 크롤링
        crawled_data_list: List[NaverBlogCrawledResponse] = []

        # 크롤링 시간 측정 시작
        crawling_start_time = time.time()

        # 멀티스레딩을 사용한 병렬 처리
        # 각 스레드에서 독립적인 WebDriver 인스턴스를 생성
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=10) as executor:
            # 각 URL에 대해 별도 스레드에서 크롤링 실행
            tasks = [
                loop.run_in_executor(executor, self._crawl_single_url, item.link)
                for item in target_items
            ]
            # 모든 작업 완료까지 대기
            results = await asyncio.gather(*tasks)

            # 성공한 결과만 수집
            for result in results:
                if "error" not in result:
                    crawled_response = NaverBlogCrawledResponse(**result)
                    crawled_data_list.append(crawled_response)

        # 크롤링 시간 측정 종료
        crawling_end_time = time.time()
        crawling_duration = crawling_end_time - crawling_start_time

        print(
            f"총 소요시간 {crawling_duration:.2f}초, 성공한 블로그 수: {len(crawled_data_list)}"
        )

        if not crawled_data_list:
            return "분석할 최신 블로그를 찾지 못했습니다. 다른 검색어로 시도해주세요."

        # 4. 크롤링된 데이터를 AI 서비스에 전달하여 분석 요청
        final_review = self.openai_service.generate_response(crawled_data_list)

        return final_review
