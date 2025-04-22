"""
Application-specific configuration using Pydantic Settings.
"""

from typing import Dict

from pydantic_settings import BaseSettings


class ValidationConfig(BaseSettings):
    """Validation thresholds and settings."""

    confidence_threshold: float = 0.7
    urgency_threshold: float = 0.8


class SystemMessages(BaseSettings):
    """System message configuration."""

    startup: Dict = {
        "banner": "🗓️ Calendar Assistant 🗓️",
        "welcome": "Type 'exit' or 'quit' to end the session",
        "log": "######## Calendar Assistant Startup ########",
    }
    shutdown: Dict = {
        "normal": "👋 Goodbye! Shutting down.",
        "interrupt": "👋 Interrupted! Shutting down.",
        "error": "💥 An unexpected error occurred: %s",
        "log": "######## Calendar Assistant Shutdown ########",
    }
    error_log: Dict = {
        "interrupt": "User interrupted the session.",
        "unexpected": "An unexpected error occurred.",
    }


class TimezoneConfig(BaseSettings):
    """Timezone configuration."""

    default_timezone: str = "UTC"


class AppConfig(BaseSettings):
    """Main application configuration."""

    validation: ValidationConfig = ValidationConfig()
    messages: SystemMessages = SystemMessages()
    timezone: TimezoneConfig = TimezoneConfig()
