"""
Datetime Utility Module

Provides reference datetime information for LLM function calls.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from app.config.settings import get_settings
from app.core.schema.event import EventDateTime


def get_datetime_reference() -> EventDateTime:
    """
    Get current datetime as reference point for LLM.
    Utilizes the configured user timezone for accurate event scheduling.

    Returns:
        EventDateTime: Current datetime in user timezone
                      with properly formatted dateTime and timeZone fields
    """
    settings = get_settings()
    user_tz = settings.app.user_timezone
    tz = ZoneInfo(user_tz)

    current = datetime.now(tz)
    current_iso = current.replace(microsecond=0).isoformat()

    return EventDateTime(dateTime=current_iso, timeZone=user_tz)
