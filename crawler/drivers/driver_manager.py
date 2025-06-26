"""
웹드라이버 설정 및 관리를 담당하는 모듈

Chrome 드라이버의 옵션 설정, 초기화, 종료를 관리
헤드리스 모드, 사용자 에이전트 등의 설정을 포함
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DriverManager:
    """
    웹드라이버 생성과 관리를 담당하는 클래스

    Chrome 드라이버의 설정을 통합 관리하고
    안정적인 드라이버 초기화 및 종료를 제공
    """

    def __init__(self, headless: bool = False, timeout: int = 10):
        """
        드라이버 매니저 초기화

        Args:
            headless: 헤드리스 모드 실행 여부
            timeout: 요소 대기 시간 (초)
        """
        self.headless = headless
        self.timeout = timeout
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None

    def create_driver(self) -> webdriver.Chrome:
        """
        Chrome 드라이버를 생성하고 설정

        Returns:
            설정된 Chrome 웹드라이버 인스턴스
        """
        options = Options()

        # 기본 옵션 설정
        if self.headless:
            options.add_argument("--headless")

        # 안정성을 위한 추가 옵션
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        # 봇 탐지 방지를 위한 설정
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            self.wait = WebDriverWait(self.driver, self.timeout)

            logger.info("Chrome 드라이버가 성공적으로 초기화되었습니다")
            return self.driver

        except Exception as e:
            logger.error(f"드라이버 생성 실패: {str(e)}")
            raise

    def quit_driver(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.wait = None
            logger.info("드라이버가 종료되었습니다")
