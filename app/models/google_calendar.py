from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class EventDateTime(BaseModel):
    """Event start and end times for Google Calendar API"""
    dateTime: str = Field(
        description="Start or end time in ISO 8601 format",
        json_schema_extra={"example": "2023-04-28T09:00:00"},
    )
    timeZone: str = Field(
        description="Time zone in IANA format",
        json_schema_extra={"example": "Australia/Sydney"},
    )

class Attendee(BaseModel):
    """Attendee information for Google Calendar API"""
    email: str = Field(
        description="Email address of an attendee",
        json_schema_extra={"example": "person@example.com"},
    )

class ReminderOverride(BaseModel):
    """Reminder override settings for Google Calendar API"""
    method: Literal["popup", "email"] = Field(description="Reminder method")
    minutes: int = Field(description="Minutes before event")

class ReminderSettings(BaseModel):
    """Reminder settings for Google Calendar API"""
    useDefault: bool = Field(description="Whether to use calendar default reminders")
    overrides: Optional[List[ReminderOverride]] = Field(
        default=None,
        description="Custom reminder overrides, required if useDefault is False",
    )

class GoogleCalendarEvent(BaseModel):
    """Google Calendar API event format"""
    summary: str = Field(description="Event title")
    start: EventDateTime
    end: EventDateTime
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: Optional[List[Attendee]] = None
    reminders: Optional[ReminderSettings] = None