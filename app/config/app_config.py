"""
App Configuration Module

Application-specific configuration using Pydantic Settings.
"""

from zoneinfo import ZoneInfo, available_timezones

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Main application configuration."""

    user_timezone: str = Field(
        description="IANA timezone (e.g., Australia/Sydney, America/New_York)",
        alias="APP_USER_TIMEZONE",
    )

    calendar_id: str = Field(
        default="primary",
        description="Calendar ID to use for operations",
        alias="APP_CALENDAR_ID",
    )

    @field_validator("user_timezone")
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        """Validate IANA timezone"""
        try:
            ZoneInfo(v)
            return v
        except Exception as exc:
            valid_zones = ", ".join(sorted(available_timezones())[:5]) + "..."
            raise ValueError(
                f"Invalid IANA timezone: {v}. Must be a valid IANA timezone (e.g., {valid_zones})"
            ) from exc

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
