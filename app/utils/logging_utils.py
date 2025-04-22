"""
Logging utilities for the Calendar Assistant.
Handles application-specific logging functionality.
"""

from typing import Dict

from app.services.log_setup import logger


def log_result(result: Dict) -> None:
    """
    Log the result of a calendar request.

    Args:
        result: Response dictionary containing status and message
    """
    if result["status"] == "success":
        logger.info("Calendar request successful: %s", result["message"])
    else:
        logger.error("Calendar request failed: %s", result["message"])
