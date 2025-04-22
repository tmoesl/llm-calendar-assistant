from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class CalendarValidation(BaseModel):
    """Check if input is a valid calendar request"""

    is_calendar_request: bool = Field(description="Whether this is a calendar request")
    confidence_score: float = Field(description="Confidence score between 0 and 1")


class SecurityCheck(BaseModel):
    """Check for prompt injection or system manipulation attempts"""

    is_safe: bool = Field(description="Whether the input appears safe")
    risk_flags: list[str] = Field(description="List of potential security concerns")


class CalendarRequestType(BaseModel):
    """Router LLM call: Determine the type of calendar request"""

    request_type: Literal[
        "new_event", "modify_event", "delete_event", "view_event", "not_actionable"
    ] = Field(description="Type of calendar request being made")
    confidence_score: float = Field(description="Confidence score between 0 and 1")
    description: str = Field(description="Description of the request type")


class EventDateTime(BaseModel):
    """Event start and end times"""

    dateTime: str = Field(
        description="Start or end time in ISO 8601 format",
        json_schema_extra={"example": "2023-04-28T09:00:00"},
    )
    timeZone: str = Field(
        description="Time zone in IANA format",
        json_schema_extra={"example": "Australia/Sydney"},
    )


class Attendee(BaseModel):
    """Attendee information for calendar events"""

    email: str = Field(
        description="Email address of an attendee",
        json_schema_extra={"example": "person@example.com"},
    )


class ReminderOverride(BaseModel):
    method: Literal["popup", "email"] = Field(description="Reminder method")
    minutes: int = Field(description="Minutes before event")


class ReminderSettings(BaseModel):
    useDefault: bool = Field(description="Whether to use calendar default reminders")
    overrides: Optional[List[ReminderOverride]] = Field(
        default=None,
        description="Custom reminder overrides, required if useDefault is False",
    )


class EventDetails(BaseModel):
    """Event details for calendar requests"""

    summary: str = Field(
        description="Professional title of the event (2-3 words)",
        json_schema_extra={"example": "Team Meeting"},
    )
    start: EventDateTime
    end: EventDateTime
    description: Optional[str] = Field(
        default=None,
        description="Description of the event",
        json_schema_extra={"example": "Discuss project updates and quarterly roadmap"},
    )
    attendees: Optional[List[Attendee]] = Field(
        default=None,
        description="List of attendees with their email addresses",
        json_schema_extra={"example": [{"email": "person@example.com"}]},
    )
    location: Optional[str] = Field(
        default=None,
        description="Location of the event",
    )
    reminders: Optional[ReminderSettings] = Field(
        default=None,
        description="Reminders for the event (use default or provide override list)",
    )
    event_id: Optional[str] = Field(
        default=None,
        description="Unique identifier for the event",
    )
