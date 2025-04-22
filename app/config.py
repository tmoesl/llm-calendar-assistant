"""
Application configuration settings for the LLM Calendar Assistant.
"""

# Core validation thresholds
CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence score to proceed with a request

# Base configuration
BASE_CONFIG = {
    "urgency_threshold": 0.8,  # Threshold for prioritizing urgent requests
}

# LLM configuration
BASE_LLM_CONFIG = {
    "model": "gpt-4o",  # Default OpenAI model to use
    "temperature": 0.1,  # Low temperature for more deterministic outputs
    "max_tokens": 1024,  # Maximum response length
}

# Timezone configuration
TIMEZONE_CONFIG = {
    "default_timezone": "UTC",  # Fallback timezone if local detection fails
}

# Application system messages
APP_SYSTEM_MESSAGES = {
    "startup": {
        "banner": "🗓️ Calendar Assistant 🗓️",
        "welcome": "Type 'exit' or 'quit' to end the session",
        "log": "######## Calendar Assistant Startup ########",
    },
    "shutdown": {
        "normal": "👋 Goodbye! Shutting down.",
        "interrupt": "👋 Interrupted! Shutting down.",
        "error": "💥 An unexpected error occurred: %s",
        "log": "######## Calendar Assistant Shutdown ########",
    },
    "error_log": {
        "interrupt": "User interrupted the session.",
        "unexpected": "An unexpected error occurred.",
    },
}
