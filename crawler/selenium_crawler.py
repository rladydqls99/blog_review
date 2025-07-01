"""
Selenium 기반 웹 크롤링의 기본 기능을 제공하는 모듈

웹페이지 로딩, 요소 검색, 데이터 추출 등의
공통적인 크롤링 작업을 수행하는 기본 클래스
"""

from selenium.webdriver.common.by import By
from typing import List
import logging

from drivers.driver_manager import DriverManager
from utils.wait_conditions import WaitConditions

logger = logging.getLogger(__name__)


class SeleniumCrawler:
    """
    Selenium을 사용한 웹 크롤링의 기본 클래스

    웹페이지 접근, 요소 검색, 데이터 추출 등의
    기본적인 크롤링 기능을 제공
    """

    def __init__(self, headless: bool = False, timeout: int = 10):
        """
        크롤러 초기화

        Args:
            headless: 헤드리스 모드 실행 여부
            timeout: 요소 대기 시간
        """
        self.driver_manager = DriverManager(headless=headless, timeout=timeout)
        self.driver = None
        self.wait_conditions = WaitConditions()

    def start(self):
        """크롤러 시작 - 드라이버 초기화"""
        try:
            self.driver = self.driver_manager.create_driver()
            logger.info("크롤러가 시작되었습니다")
        except Exception as e:
            logger.error(f"크롤러 시작 실패: {str(e)}")
            raise

    def stop(self):
        """크롤러 종료 - 드라이버 정리"""
        if self.driver_manager:
            self.driver_manager.quit_driver()
            self.driver = None
            logger.info("크롤러가 종료되었습니다")

    def get_page(self, url: str, wait_for_load: bool = True) -> bool:
        """
        웹페이지 로드

        Args:
            url: 접근할 URL
            wait_for_load: 페이지 로딩 완료까지 대기 여부

        Returns:
            로딩 성공 여부
        """
        if not self.driver:
            raise RuntimeError(
                "크롤러가 시작되지 않았습니다. start() 메서드를 먼저 호출하세요."
            )

        try:
            logger.info(f"페이지 로딩 시작: {url}")
            self.driver.get(url)

            if wait_for_load:
                success = self.wait_conditions.wait_for_page_load(self.driver)
                if not success:
                    logger.warning("페이지 로딩 완료 대기 실패")
                    return False

            logger.info("페이지 로딩 완료")
            return True

        except Exception as e:
            logger.error(f"페이지 로딩 실패: {str(e)}")
            return False

    def find_element_safe(self, by: By, value: str, timeout: int = 10):
        """
        안전한 요소 검색 (예외 처리 포함)

        Args:
            by: 검색 방법
            value: 검색 값
            timeout: 대기 시간

        Returns:
            찾은 요소 또는 None
        """
        try:
            element = self.wait_conditions.wait_for_element(
                self.driver, by, value, timeout
            )
            if element:
                logger.debug(f"요소 검색 성공: {value}")
                return element
            else:
                logger.warning(f"요소 검색 실패: {value}")
                return None
        except Exception as e:
            logger.error(f"요소 검색 중 오류: {str(e)}")
            return None

    def find_elements_safe(self, by: By, value: str) -> List:
        """
        안전한 다중 요소 검색

        Args:
            by: 검색 방법
            value: 검색 값

        Returns:
            찾은 요소들의 리스트
        """
        if not self.driver:
            return []

        try:
            elements = self.driver.find_elements(by, value)
            logger.debug(f"다중 요소 검색 성공: {len(elements)}개 발견")
            return elements
        except Exception as e:
            logger.error(f"다중 요소 검색 중 오류: {str(e)}")
            return []

    def extract_text(self, element) -> str:
        """
        요소에서 텍스트 추출

        Args:
            element: 웹 요소

        Returns:
            추출된 텍스트
        """
        try:
            return element.text.strip() if element else ""
        except Exception as e:
            logger.error(f"텍스트 추출 중 오류: {str(e)}")
            return ""

    def __enter__(self):
        """컨텍스트 매니저 진입"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.stop()
