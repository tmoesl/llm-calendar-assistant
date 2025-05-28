"""
App Configuration Module

Application-specific configuration using Pydantic Settings.
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    """Main application configuration."""

    confidence_threshold: float = Field(
        default=0.7,
        description="Minimum confidence level for validation.",
    )
    default_calendar_id: str = Field(
        default="primary",
        description="Default calendar ID to use for operations.",
    )
