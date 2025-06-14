"""
Settings Module

Main settings for the application using Pydantic Settings.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.llm_config import LLMConfig


class Settings(BaseSettings):
    """Main settings for the application."""

    llm: LLMConfig = Field(default_factory=LLMConfig)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """
    Get the application settings. Uses lru_cache to avoid repeated loading

    Returns:
        Settings: The application settings.
    """
    return Settings()
