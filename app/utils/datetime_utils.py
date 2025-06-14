"""
Datetime Utility Module

Provides reference datetime information for LLM function calls.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from app.calendar.config import get_calendar_config
from app.core.schema.event import EventDateTime


def get_datetime_reference() -> EventDateTime:
    """
    Get current datetime as reference point for LLM.
    Utilizes the configured user timezone for accurate event scheduling.

    Returns:
        EventDateTime: Current datetime in user timezone
                      with properly formatted dateTime and timeZone fields
    """
    config = get_calendar_config()
    user_tz = config.user_timezone
    tz = ZoneInfo(user_tz)

    current = datetime.now(tz)
    current_iso = current.replace(microsecond=0).isoformat()

    return EventDateTime(dateTime=current_iso, timeZone=user_tz)
