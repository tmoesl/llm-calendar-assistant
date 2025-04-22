"""
Logging setup and initialization.
Handles the configuration and setup of logging for the application.
"""

import logging
import sys
from pathlib import Path

from app.services.log_config import get_log_config

# Create a logger object and settings
config = get_log_config()
logger = logging.getLogger(config.name)


def configure_logging() -> None:
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
configure_logging()
