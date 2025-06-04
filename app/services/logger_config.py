"""
Logging Configuration

Contains configuration classes, constants, and settings for the logging system.
Pure configuration - no runtime behavior or logger creation.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings

# Service name constants
API = "api"
WORKER = "celery"
PIPELINE = "pipeline"


class LogConfig(BaseSettings):
    """Logging configuration with environment variable support.
    All settings can be overridden with LOG_ prefixed environment variables.
    """

    name: str = "calendar_assistant"
    level: str = "DEBUG"
    format: str = "%(asctime)s | %(levelname)s | %(service_tag)s %(request_id)s %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    file_path: str = "logs/calendar_assistant.log"
    console_output: bool = True
    file_output: bool = True
    propagate: bool = False


@lru_cache
def get_log_config() -> LogConfig:
    """
    Get the logging configuration. Uses lru_cache to avoid repeated loading

    Returns:
        LogConfig: The logging configuration.
    """
    return LogConfig()
