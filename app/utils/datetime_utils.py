"""
Datetime utility functions for the Calendar Assistant.
Handles timezone and datetime operations.
"""

import datetime
from typing import Dict

import pytz
from tzlocal import get_localzone_name


def get_current_datetime_info() -> Dict[str, str]:
    """
    Provides current date, time, and timezone information.
    Used for timezone context and default values.

    Returns:
        dict: Current datetime and timezone information
    """
    try:
        timezone_str = get_localzone_name()  # e.g., 'Australia/Sydney'
        timezone = pytz.timezone(timezone_str)
        now_local = datetime.datetime.now(timezone)

        return {"current_datetime": now_local.isoformat(), "timezone": timezone_str}

    except Exception:
        # Fallback if local timezone detection fails
        now_utc = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=pytz.utc)
        return {"current_datetime": now_utc.isoformat(), "timezone": "UTC"}