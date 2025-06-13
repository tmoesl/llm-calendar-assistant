"""
Logging Configuration

Contains configuration classes, constants, and settings for the logging system.
Pure configuration - no runtime behavior or logger creation.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Service name constants
API = "api"
WORKER = "celery"
PIPELINE = "pipeline"


class LogConfig(BaseSettings):
    """Logging configuration with environment variable support."""

    # Environment-specific configuration
    level: str = Field(default="DEBUG", alias="LOG_LEVEL")
    console_output: bool = Field(default=True, alias="LOG_CONSOLE_OUTPUT")
    file_output: bool = Field(default=True, alias="LOG_FILE_OUTPUT")

    # Application constants (hardcoded)
    name: str = "calendar_assistant"
    file_path: str = "logs/calendar_assistant.log"

    # --- Production Standards (hardcoded) ---
    format: str = "%(asctime)s | %(levelname)s | %(service_tag)s %(request_id)s %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    propagate: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_log_config() -> LogConfig:
    """
    Get the logging configuration. Uses lru_cache to avoid repeated loading

    Returns:
        LogConfig: The logging configuration.
    """
    return LogConfig()
