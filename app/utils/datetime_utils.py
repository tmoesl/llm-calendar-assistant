"""
Datetime Utility Module

Provides reference datetime information for LLM function calls.
"""

from datetime import datetime

import pytz
from tzlocal import get_localzone_name

from app.core.schema.event import EventDateTime
from app.services.logger_factory import logger


def get_datetime_reference() -> EventDateTime:
    """
    Get current datetime as reference point for LLM.
    Uses system timezone with UTC fallback.

    Returns:
        EventDateTime: Current datetime in system timezone or UTC fallback
                      with properly formatted dateTime and timeZone fields
    """
    try:
        # Get system timezone
        system_tz = get_localzone_name()
        tz = pytz.timezone(system_tz)

        # Get current time in that timezone
        current = datetime.now(tz)

        # Format for LLM reference (remove microseconds for cleaner output)
        current_iso = current.replace(microsecond=0).isoformat()

        return EventDateTime(dateTime=current_iso, timeZone=system_tz)

    except Exception as e:
        logger.warning("System timezone detection failed: %s. Using UTC.", str(e))
        current_utc = datetime.now(pytz.UTC)

        return EventDateTime(
            dateTime=current_utc.replace(microsecond=0).isoformat(), timeZone="UTC"
        )
