"""
네이버 블로그 전용 크롤링 모듈

네이버 블로그의 특수한 구조(iframe 등)를 고려한
전문적인 크롤링 기능을 제공
"""

from selenium.webdriver.common.by import By
from typing import Dict, Any
import logging
import time

from .selenium_crawler import SeleniumCrawler

logger = logging.getLogger(__name__)


class NaverBlogCrawler(SeleniumCrawler):
    """
    네이버 블로그 전용 크롤러

    네이버 블로그의 iframe 구조와 특수한 요소들을
    고려한 전문적인 크롤링 기능 제공
    """

    def __init__(self, headless: bool = False):
        """
        네이버 블로그 크롤러 초기화

        Args:
            headless: 헤드리스 모드 실행 여부
        """
        super().__init__(headless=headless, timeout=15)

    def get_blog_content(self, url: str) -> Dict[str, Any]:
        """
        네이버 블로그 포스트의 내용을 추출

        Args:
            url: 네이버 블로그 포스트 URL

        Returns:
            블로그 포스트 정보 딕셔너리
        """
        if not self.get_page(url):
            return {"error": "페이지 로딩 실패"}

        # 네이버 블로그 컨텐츠 로딩 대기
        if not self.wait_conditions.wait_for_naver_blog_content(self.driver):
            logger.warning("네이버 블로그 컨텐츠 로딩 대기 실패")

        # 추가 대기 (네이버 블로그는 로딩이 오래 걸림)
        time.sleep(3)

        try:
            # iframe으로 전환 시도
            iframe_switched = self._switch_to_content_iframe()

            # 블로그 정보 추출
            blog_data = {
                "title": self._extract_title(),
                "content": self._extract_content(),
                "author": self._extract_author(),
                "date": self._extract_date(),
                "address": self._extract_address(),
                "url": url,
                "iframe_used": iframe_switched,
            }

            # 메인 프레임으로 복귀
            if iframe_switched:
                self.driver.switch_to.default_content()

            return blog_data

        except Exception as e:
            logger.error(f"블로그 컨텐츠 추출 실패: {str(e)}")
            return {"error": f"컨텐츠 추출 실패: {str(e)}"}

    def _switch_to_content_iframe(self) -> bool:
        """
        네이버 블로그의 메인 컨텐츠 iframe으로 전환

        Returns:
            iframe 전환 성공 여부
        """
        try:
            # 가능한 iframe 선택자들
            iframe_selectors = [
                "mainFrame",  # ID로 찾기
                "//iframe[@id='mainFrame']",  # XPath로 찾기
                "iframe[src*='blog.naver.com']",  # CSS 선택자
            ]

            for selector in iframe_selectors:
                try:
                    if selector.startswith("//"):
                        iframe = self.find_element_safe(By.XPATH, selector, timeout=5)
                    elif selector.startswith("iframe"):
                        iframe = self.find_element_safe(
                            By.CSS_SELECTOR, selector, timeout=5
                        )
                    else:
                        iframe = self.find_element_safe(By.ID, selector, timeout=5)

                    if iframe:
                        self.driver.switch_to.frame(iframe)
                        logger.info("iframe으로 전환 성공")
                        return True
                except Exception as e:
                    logger.debug(f"iframe 전환 시도 실패 ({selector}): {str(e)}")
                    continue

            logger.info("iframe을 찾지 못했습니다. 메인 페이지에서 진행합니다.")
            return False

        except Exception as e:
            logger.error(f"iframe 전환 중 오류: {str(e)}")
            return False

    def _extract_title(self) -> str:
        """블로그 포스트 제목 추출"""
        title_selectors = [
            "//h1[contains(@class, 'title')]",
            "//h2[contains(@class, 'title')]",
            "//div[contains(@class, 'se-title')]",
            "//span[contains(@class, 'title')]",
            "//*[@class='se-title-text']",
            "//title",
        ]

        for selector in title_selectors:
            element = self.find_element_safe(By.XPATH, selector, timeout=3)
            if element:
                title = self.extract_text(element)
                if title and len(title.strip()) > 0:
                    logger.debug(f"제목 추출 성공: {title[:50]}...")
                    return title

        logger.warning("제목을 찾을 수 없습니다")
        return ""

    def _extract_content(self) -> str:
        """블로그 포스트 본문 추출"""
        content_selectors = [
            "//div[contains(@class, 'se-main-container')]",
            "//div[contains(@class, 'post-view')]",
            "//div[contains(@class, 'blog-content')]",
            "//div[@id='post-view']",
            "//div[contains(@class, 'se-component')]",
        ]

        for selector in content_selectors:
            element = self.find_element_safe(By.XPATH, selector, timeout=3)
            if element:
                content = self.extract_text(element)
                if content and len(content.strip()) > 20:  # 최소 길이 확인
                    logger.debug(f"본문 추출 성공: {len(content)}자")
                    return content

        logger.warning("본문을 찾을 수 없습니다")
        return ""

    def _extract_author(self) -> str:
        """블로그 작성자 추출"""
        author_selectors = [
            "//span[contains(@class, 'author')]",
            "//span[contains(@class, 'nick')]",
            "//div[contains(@class, 'blog-name')]",
            "//a[contains(@class, 'blogger')]",
        ]

        for selector in author_selectors:
            element = self.find_element_safe(By.XPATH, selector, timeout=2)
            if element:
                author = self.extract_text(element)
                if author:
                    return author

        return ""

    def _extract_date(self) -> str:
        """작성일 추출"""
        date_selectors = [
            "//span[contains(@class, 'date')]",
            "//span[contains(@class, 'se_publishDate')]",
            "//div[contains(@class, 'post-date')]",
            "//time",
        ]

        for selector in date_selectors:
            element = self.find_element_safe(By.XPATH, selector, timeout=2)
            if element:
                date = self.extract_text(element)
                if date:
                    return date

        return ""

    def _extract_address(self) -> str:
        """주소 추출"""
        address_selectors = [
            "//p[contains(@class, 'se-map-address')]",
            "//span[contains(@class, 'se-map-address')]",
            "//div[contains(@class, 'se-map-address')]",
            "//span[contains(@class, 'se-map-address')]",
        ]

        for selector in address_selectors:
            element = self.find_element_safe(By.XPATH, selector, timeout=2)
            if element:
                address = self.extract_text(element)
                if address:
                    return address
        return ""
