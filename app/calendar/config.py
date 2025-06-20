"""
Calendar Configuration Module

Google Calendar specific configuration using Pydantic Settings.
"""

from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo, available_timezones

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class CalendarConfig(BaseSettings):
    """Google Calendar configuration."""

    # Calendar Operations
    calendar_id: str = Field(
        default="primary",
        description="Calendar ID to use for operations",
        alias="CALENDAR_ID",
    )

    user_timezone: str = Field(
        default="Australia/Sydney",
        description="IANA timezone for user's calendar operations",
        alias="CALENDAR_USER_TIMEZONE",
    )

    # OAuth Authentication Paths (mounts to /app/tokens/token.json in docker-compose.yml)
    token_path: Path = Field(
        default=Path("tokens/token.json"),
        description="Path to store OAuth refresh token",
        alias="CALENDAR_TOKEN_PATH",
    )

    # OAuth Authentication Paths (mounts to /app/credentials.json in docker-compose.yml)
    credentials_path: Path = Field(
        default=Path("credentials.json"),
        description="Path to Google OAuth client credentials file",
        alias="CALENDAR_CREDENTIALS_PATH",
    )

    # API Configuration
    api_name: str = Field(
        default="calendar",
        description="Google API service name",
        alias="CALENDAR_API_NAME",
    )

    api_version: str = Field(
        default="v3",
        description="Google Calendar API version",
        alias="CALENDAR_API_VERSION",
    )

    scopes: list[str] = Field(
        default=["https://www.googleapis.com/auth/calendar"],
        description="Google Calendar API scopes",
        alias="CALENDAR_SCOPES",
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
            raise ValueError(f"Invalid timezone: {v}. Valid: {valid_zones}") from exc

    @field_validator("token_path", "credentials_path")
    @classmethod
    def validate_paths(cls, v: Path) -> Path:
        """Ensure paths are Path objects"""
        return Path(v) if not isinstance(v, Path) else v

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_calendar_config() -> CalendarConfig:
    """
    Get the calendar configuration. Uses lru_cache to avoid repeated loading

    Returns:
        CalendarConfig: The calendar configuration.
    """
    return CalendarConfig()
