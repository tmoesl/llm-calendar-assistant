"""
App Configuration Module

Application-specific configuration using Pydantic Settings.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Main application configuration."""

    confidence_threshold: float = Field(
        default=0.7,
        alias="APP_CONFIDENCE_THRESHOLD",
    )
    default_calendar_id: str = Field(
        default="primary",
        alias="APP_DEFAULT_CALENDAR_ID",
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
