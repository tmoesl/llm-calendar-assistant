"""
Pipeline orchestration for calendar requests.
Coordinates the processing steps without implementing business logic.
"""

from typing import Dict

from app.config.settings import get_settings
from app.handlers.event_handlers import get_handler_for_type
from app.pipeline.router import route_request
from app.pipeline.validators import validate_user_input
from app.utils.logging_config import logger

# Initialize settings
settings = get_settings()
confidence_threshold = settings.app.validation.confidence_threshold


def handle_calendar_request(input_text: str) -> Dict:
    """
    Main entry point for handling calendar requests.
    Validates input and initiates the processing pipeline.

    Args:
        input_text: Natural language user request

    Returns:
        Response dictionary with status, message, and any relevant data
    """
    if not input_text or not input_text.strip():
        return {
            "status": "error",
            "message": "Please provide a calendar request.",
            "data": None,
        }

    logger.info("Calendar request received: %s", input_text)

    # Process the request through our pipeline
    return process_calendar_request(input_text)


def process_calendar_request(user_input: str) -> Dict:
    """
    Main pipeline for processing calendar requests.
    Implements the core AI workflow from the PRD.

    Args:
        user_input: Natural language user request

    Returns:
        Response dictionary with status, message, and any relevant data
    """
    logger.info(">>>> Request processing pipeline started")

    # Steps 1 & 2: Validate input
    is_valid, validation_message = validate_user_input(user_input)
    if not is_valid:
        return {"status": "error", "message": validation_message, "data": None}

    logger.info("Validation checks completed")

    # Step 3: Route the request to determine intent
    try:
        request_type, confidence_score = route_request(user_input)

        if confidence_score < confidence_threshold:
            return {
                "status": "error",
                "message": "I'm not confident about what you're asking. Could you be more specific?",
                "data": None,
            }

        # Step 4: Get and execute the appropriate handler
        handler = get_handler_for_type(request_type)
        if not handler:
            return {
                "status": "error",
                "message": "I couldn't determine how to handle your calendar request.",
                "data": None,
            }

        logger.info("Routing to associated handler completed (type: %s)", request_type)

        result = handler(user_input)
        logger.info("Event handler executed (type: %s)", request_type)

        logger.info("<<<< Request processing pipeline completed")
        return result

    except Exception as e:
        logger.error("Error in request pipeline: %s", str(e))
        return {
            "status": "error",
            "message": "An error occurred while processing your request.",
            "data": None,
        }
