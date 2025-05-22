"""
Datetime Utility Module

Provides reference datetime information for LLM function calls.
"""

from datetime import datetime

import pytz
from tzlocal import get_localzone_name

from app.services.log_service import logger


def get_datetime_reference() -> dict[str, str]:
    """
    Get current datetime as reference point for LLM.
    Uses system timezone with UTC fallback.

    Returns:
        dict: {
            "current_datetime": ISO format datetime string,
            "timezone": IANA timezone string
        }
    """
    try:
        # Get system timezone
        system_tz = get_localzone_name()
        tz = pytz.timezone(system_tz)

        # Get current time in that timezone
        current = datetime.now(tz)

        # Format for LLM reference (remove microseconds for cleaner output)
        current_iso = current.replace(microsecond=0).isoformat()

        return {"current_datetime": current_iso, "timezone": system_tz}

    except Exception as e:
        logger.warning("System timezone detection failed: %s. Using UTC.", str(e))
        current_utc = datetime.now(pytz.UTC)

        return {
            "current_datetime": current_utc.replace(microsecond=0).isoformat(),
            "timezone": "UTC",
        }
