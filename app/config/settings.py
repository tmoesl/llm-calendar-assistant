from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from app.config.app_config import AppConfig
from app.config.llm_config import LLMConfig

load_dotenv()

"""
Main settings for the application using Pydantic Settings.
"""


class Settings(BaseSettings):
    """Main settings for the application."""

    app_name: str = "GenAI Calendar Assistant"
    llm: LLMConfig = LLMConfig()
    app: AppConfig = AppConfig()


@lru_cache
def get_settings() -> Settings:
    """
    Get the application settings. Uses lru_cache to avoid repeated loading

    Returns:
        Settings: The application settings.
    """
    return Settings()
