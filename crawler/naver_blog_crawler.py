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

    # 선택자들을 상수로 관리하여 가독성 및 유지보수성 향상
    IFRAME_SELECTORS = (
        "mainFrame",  # ID로 찾기
        "//iframe[@id='mainFrame']",  # XPath로 찾기
        "iframe[src*='blog.naver.com']",  # CSS 선택자
    )
    TITLE_SELECTORS = (
        "//h1[contains(@class, 'title')]",
        "//h2[contains(@class, 'title')]",
        "//div[contains(@class, 'se-title')]",
        "//span[contains(@class, 'title')]",
        "//*[@class='se-title-text']",
        "//title",
    )
    CONTENT_SELECTORS = (
        "//div[contains(@class, 'se-main-container')]",
        "//div[contains(@class, 'post-view')]",
        "//div[contains(@class, 'blog-content')]",
        "//div[@id='post-view']",
        "//div[contains(@class, 'se-component')]",
    )
    AUTHOR_SELECTORS = (
        "//span[contains(@class, 'author')]",
        "//span[contains(@class, 'nick')]",
        "//div[contains(@class, 'blog-name')]",
        "//a[contains(@class, 'blogger')]",
    )
    DATE_SELECTORS = (
        "//span[contains(@class, 'date')]",
        "//span[contains(@class, 'se_publishDate')]",
        "//div[contains(@class, 'post-date')]",
        "//time",
    )
    ADDRESS_SELECTORS = (
        "//p[contains(@class, 'se-map-address')]",
        "//span[contains(@class, 'se-map-address')]",
        "//div[contains(@class, 'se-map-address')]",
    )

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

        # 네이버 블로그 컨텐츠 로딩을 명시적으로 대기합니다.
        # time.sleep()을 제거하여 코드의 의도를 명확히 합니다.
        if not self.wait_conditions.wait_for_naver_blog_content(self.driver):
            logger.warning("네이버 블로그 컨텐츠 로딩 대기 실패")
            # 실패하더라도 크롤링을 시도해볼 수 있으므로 계속 진행

        try:
            # iframe으로 전환 시도
            iframe_switched = self._switch_to_content_iframe()

            # 블로그 정보 추출
            blog_data = {
                "title": self._extract_info(self.TITLE_SELECTORS),
                "content": self._extract_info(self.CONTENT_SELECTORS, min_length=20),
                "author": self._extract_info(self.AUTHOR_SELECTORS),
                "date": self._extract_info(self.DATE_SELECTORS),
                "address": self._extract_info(self.ADDRESS_SELECTORS),
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
            for selector in self.IFRAME_SELECTORS:
                try:
                    by = By.ID
                    if selector.startswith("//"):
                        by = By.XPATH
                    elif selector.startswith("iframe"):
                        by = By.CSS_SELECTOR

                    iframe = self.find_element_safe(by, selector, timeout=5)
                    if iframe:
                        self.driver.switch_to.frame(iframe)
                        logger.info(f"iframe으로 전환 성공: {selector}")
                        return True
                except Exception as e:
                    logger.debug(f"iframe 전환 시도 실패 ({selector}): {str(e)}")
                    continue

            logger.info("iframe을 찾지 못했습니다. 메인 페이지에서 진행합니다.")
            return False

        except Exception as e:
            logger.error(f"iframe 전환 중 오류: {str(e)}")
            return False

    def _extract_info(self, selectors: tuple, min_length: int = 1) -> str:
        """
        주어진 선택자 리스트를 사용하여 정보를 추출하는 범용 메서드

        Args:
            selectors: 시도할 선택자들의 튜플
            min_length: 유효한 텍스트로 간주할 최소 길이

        Returns:
            추출된 텍스트 또는 빈 문자열
        """
        for selector in selectors:
            # 네이버 블로그는 대부분의 콘텐츠가 XPATH로 식별 가능
            element = self.find_element_safe(By.XPATH, selector, timeout=2)
            if element:
                text = self.extract_text(element)
                if text and len(text.strip()) >= min_length:
                    logger.debug(f"정보 추출 성공: {selector}")
                    return text

        logger.warning(f"정보를 찾을 수 없습니다. 시도한 선택자: {selectors}")
        return ""
