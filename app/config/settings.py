"""
Settings Module

Main settings for the application using Pydantic Settings.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Main settings for the application."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """
    Get the application settings. Uses lru_cache to avoid repeated loading

    Returns:
        Settings: The application settings.
    """
    return Settings()
