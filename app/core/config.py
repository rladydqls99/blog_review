"""
애플리케이션의 모든 설정을 중앙에서 관리하는 모듈입니다.

pydantic-settings를 사용하여 .env 파일에서 환경 변수를 로드하고,
애플리케이션 전역에서 사용될 설정 객체를 제공합니다.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    애플리케이션의 모든 환경 변수를 정의하는 통합 설정 클래스
    """

    # Naver API Settings
    naver_client_id: str
    naver_client_secret: str

    # OpenAI API Settings
    open_ai_api_key: str

    # pydantic-settings 설정
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", frozen=True)
