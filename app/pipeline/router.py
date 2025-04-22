"""
Request routing logic for calendar operations.
Handles request classification and routing to appropriate handlers.
"""

from typing import Tuple

from app.llm.processor import route_calendar_request
from app.services.log_setup import logger


def route_request(user_input: str) -> Tuple[str, float]:
    """
    Route the calendar request to determine the type of operation.

    Args:
        user_input: Natural language user request

    Returns:
        Tuple of (request_type, confidence_score)
    """
    route_result = route_calendar_request(user_input)
    logger.info(
        "Type identified (type: %s, confidence: %.2f)",
        route_result.request_type,
        route_result.confidence_score,
    )
    return route_result.request_type, route_result.confidence_score
