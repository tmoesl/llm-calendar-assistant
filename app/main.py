"""
Main application entry point for the LLM Calendar Assistant.
This module provides a simple interface to interact with the calendar assistant.
"""

from app.config.settings import get_settings
from app.demo import run_demo
from app.pipeline.workflow import handle_calendar_request
from app.utils.cli_utils import print_result, print_with_border
from app.utils.logging_config import logger
from app.utils.logging_utils import log_result

# Initialize settings
settings = get_settings()
app_messages = settings.app.messages


def startup(
    message: str = app_messages.startup["banner"], border_char: str = "="
) -> None:
    """Initialize and display the calendar assistant startup message.

    Args:
        message: The message to display at startup
        border_char: Character to use for the message border
    """
    print_with_border(message, border_char, 60)
    print(app_messages.startup["welcome"])
    logger.info(app_messages.startup["log"])


def shutdown(message: str, border_char: str = "=", error: bool = False) -> None:
    """Handle application shutdown with appropriate messaging.

    Args:
        message: The message to display during shutdown
        border_char: Character to use for the message border
        error: Whether this is an error-based shutdown
    """
    print_with_border(message, border_char, 60)
    if error:
        logger.exception(app_messages.error_log["unexpected"])
    logger.info(app_messages.shutdown["log"])


def run_application() -> None:
    """Run the main application loop.
    Handles user input, processing, and result display.
    """
    while True:
        try:
            # Make input prompt more visible
            print("\n>>> ", end="", flush=True)
            user_input = input()

            if user_input.lower() in ["exit", "quit"]:
                shutdown(app_messages.shutdown["normal"])
                break

            # Print processing message with consistent spacing
            print("\n" + "-" * 60)  # Add newline before separator
            print(f"🔄 Processing: '{user_input}'")
            print("-" * 60 + "\n")  # Add newline after separator

            result = handle_calendar_request(user_input)
            log_result(result)  # Log first
            print_result(result)  # Print second

        except KeyboardInterrupt:
            shutdown(app_messages.shutdown["interrupt"])
            logger.info(app_messages.error_log["interrupt"])
            break
        except Exception as e:
            shutdown(app_messages.shutdown["error"] % str(e), "!", True)
            break


def main() -> None:
    """Execute the calendar assistant application."""
    # Initialize the application
    startup()

    # Run demo
    run_demo()

    # Start main application loop
    run_application()


if __name__ == "__main__":
    main()
