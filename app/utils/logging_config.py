"""
Centralized logging configuration for the LLM Calendar Assistant.
This ensures consistent logging across all modules.
"""

import logging
import os
import sys
from pathlib import Path

# Create a logger object
logger = logging.getLogger("calendar_assistant")

# Flag to track if logger has been configured
_is_configured = False


def configure_logging():
    """Configure logging for the application. Should be called only once at startup."""
    global _is_configured

    if _is_configured:
        return

    # Ensure logs directory exists
    logs_dir = Path(__file__).parents[2] / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Set up logging configuration
    logger.setLevel(logging.INFO)

    # Create formatters
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Create handlers
    file_handler = logging.FileHandler(logs_dir / "calendar_assistant.log")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    # Prevent propagation to root logger to avoid duplicate logs
    logger.propagate = False

    # Mark as configured
    _is_configured = True

    logger.info("Logging system initialized")


# Configure logging when this module is imported
configure_logging()
