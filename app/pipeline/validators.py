"""
Validation logic for calendar requests.
Combines LLM validations with business rules.
"""

from typing import Tuple

from app.config.settings import get_settings
from app.llm.processor import security_check, validate_calendar_request
from app.services.log_setup import logger

# Initialize settings
settings = get_settings()
confidence_threshold = settings.app.validation.confidence_threshold


def validate_user_input(user_input: str) -> Tuple[bool, str]:
    """
    Validate user input for safety and relevance to calendar operations.
    Implements PRD steps 1 & 2: User Input and Async High-Level Validation & Security.

    Args:
        user_input: Natural language user request

    Returns:
        Tuple of (is_valid, reason) where reason explains validation failures
    """
    # Step 1: Check if input is a calendar request
    calendar_validation = validate_calendar_request(user_input)
    if not calendar_validation.is_calendar_request:
        return False, "This doesn't appear to be a calendar-related request."

    if calendar_validation.confidence_score < confidence_threshold:
        return (
            False,
            "I'm not confident that this is a calendar request. Please be more specific.",
        )

    # Step 2: Security check to prevent malicious inputs
    security_validation = security_check(user_input)
    if not security_validation.is_safe:
        risk_flags = ", ".join(security_validation.risk_flags)
        logger.warning("Security validation failed with flags: %s", risk_flags)
        return False, "I cannot process this request due to security concerns."

    return True, ""
