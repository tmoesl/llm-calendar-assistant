"""
Log Service Module

Handles configuration and setup of logging for the application.
"""

import logging
import sys
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class LogConfig(BaseSettings):
    """Logging configuration with environment variable support.
    All settings can be overridden with LOG_ prefixed environment variables.
    """

    name: str = "calendar_assistant"
    level: str = "DEBUG"
    format: str = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    file_path: str = "logs/calendar_assistant.log"
    console_output: bool = True
    file_output: bool = True
    propagate: bool = False
    is_configured: bool = False


@lru_cache
def get_log_config() -> LogConfig:
    """
    Get the logging configuration. Uses lru_cache to avoid repeated loading

    Returns:
        LogConfig: The logging configuration.
    """
    return LogConfig()


# Create a logger object and settings
config = get_log_config()
logger = logging.getLogger(config.name)


def setup_logging() -> None:
    """Configure logging for the application. Should be called only once at startup."""
    if config.is_configured:
        return

    # Set up logging configuration
    logger.setLevel(getattr(logging, config.level))

    # Create formatters
    formatter = logging.Formatter(
        config.format,
        datefmt=config.date_format,
    )

    # Create and add handlers based on configuration
    if config.file_output:
        # Ensure logs directory exists
        log_path = Path(config.file_path)
        log_path.parent.mkdir(exist_ok=True)

        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if config.console_output:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    # Set propagation based on configuration
    logger.propagate = config.propagate

    # Mark as configured
    config.is_configured = True

    logger.info("Logging system initialized")


# Configure logging when this module is imported
setup_logging()
