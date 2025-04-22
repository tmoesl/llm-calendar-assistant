"""
Demo functionality for the Calendar Assistant.
Contains demo query execution and error handling.
"""

from app.pipeline.workflow import handle_calendar_request
from app.services.log_setup import logger
from app.utils.cli_utils import print_result, print_with_border
from app.utils.logging_utils import log_result

# Default demo query
DEFAULT_DEMO_QUERY = (
    "Schedule a team meeting tomorrow at 3pm with Tom about the Q2 roadmap"
)


def run_demo() -> None:
    """Run the calendar assistant demo with a sample query."""
    print("\n>>> " + DEFAULT_DEMO_QUERY + " (DEMO QUERY)")

    print("\n" + "-" * 60)  # Add newline before separator
    print(f"🔄 Processing: '{DEFAULT_DEMO_QUERY}'")
    print("-" * 60 + "\n")  # Add newline after separator

    try:
        result = handle_calendar_request(DEFAULT_DEMO_QUERY)
        log_result(result)  # Log first
        print_result(result)  # Print second
    except Exception as e:
        print_with_border(f"💥 Demo failed with error: {str(e)}", "!", 60)
        logger.exception("Error in demo")
