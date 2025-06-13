"""
App Configuration Module

Application-specific configuration using Pydantic Settings.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Main application configuration."""

    calendar_id: str = Field(
        default="primary",
        description="Calendar ID to use for operations",
        alias="APP_CALENDAR_ID",
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
