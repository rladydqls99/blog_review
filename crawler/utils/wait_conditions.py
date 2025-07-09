"""
Selenium 대기 조건을 정의하는 모듈

페이지 로딩, 요소 출현 등의 다양한 대기 조건을 제공
네이버 블로그 특화 대기 조건도 포함
"""

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
import logging

logger = logging.getLogger(__name__)


class WaitConditions:
    @staticmethod
    def wait_for_element(driver: WebDriver, by: By, value: str, timeout: int = 10):
        try:
            wait = WebDriverWait(driver, timeout)
            return wait.until(EC.presence_of_element_located((by, value)))
        except Exception:
            return None

    @staticmethod
    def wait_for_page_load(driver: WebDriver, timeout: int = 10):
        try:
            wait = WebDriverWait(driver, timeout)
            wait.until(
                lambda driver: driver.execute_script("return document.readyState")
                == "complete"
            )
            return True
        except Exception:
            return False

    @staticmethod
    def wait_for_naver_blog_content(driver: WebDriver, timeout: int = 15):
        try:
            wait = WebDriverWait(driver, timeout)

            # 가능한 컨테이너 요소들 (네이버 블로그 구조 변경 대응)
            possible_selectors = [
                "//iframe[@id='mainFrame']",  # 메인 프레임
                "//*[@class='se-main-container']",  # 스마트에디터 컨테이너
                "//*[contains(@class, 'post-view')]",  # 포스트 뷰
                "//*[contains(@class, 'blog-content')]",  # 블로그 컨텐츠
                "//*[@id='post-view']",  # 포스트 뷰 ID
            ]

            for selector in possible_selectors:
                try:
                    element = wait.until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    if element:
                        return True
                except Exception:
                    continue

            return False

        except Exception as e:
            logger.error(f"네이버 블로그 컨텐츠 대기 실패: {str(e)}")
            return False
