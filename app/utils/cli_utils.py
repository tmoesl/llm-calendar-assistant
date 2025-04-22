"""
CLI utility functions for the Calendar Assistant.
Handles terminal output formatting and response display.
"""

from typing import Dict


def print_with_border(message: str, border_char="=", width=80) -> None:
    """
    Print message with a border for better visibility in terminal.

    Args:
        message: The message to print
        border_char: Character to use for the border
        width: Width of the border
    """
    border = border_char * width
    print(f"\n{border}")
    print(message)
    print(f"{border}\n")


def print_result(response: Dict) -> None:
    """
    Display the result of a calendar request in the terminal.

    Args:
        response: Response dictionary containing status and message
    """
    if response["status"] == "success":
        print_with_border(f"✅ SUCCESS: {response['message']}", "-", 60)
    else:
        print_with_border(f"❌ ERROR: {response['message']}", "-", 60)
