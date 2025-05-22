"""
Google Calendar API Schema Module

Defines the schema for Google Calendar API requests and converts validated LLM-generated event
models to the API format. Validation is done by pydantic models that are used as response models
for the LLM call.
"""

from typing import Self

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.core.schema.llm import (
    LlmCreateEvent,
    LlmEventLookup,
)


class GoogleDateTime(BaseModel):
    """
    Google Calendar API datetime specification.
    Supports both date-time and date-only formats.
    """

    dateTime: str | None = None
    date: str | None = None
    timeZone: str | None = None

    @model_validator(mode="after")
    def validate_fields(self) -> Self:
        """Validate API-specific requirements"""
        if self.date:
            if self.dateTime or self.timeZone:
                raise ValueError("All-day event must use 'date' only, not 'dateTime' or 'timeZone'")
        elif self.dateTime and not self.timeZone:
            raise ValueError("Time-specific event requires timeZone")
        return self


class GoogleAttendee(BaseModel):
    """Google Calendar API attendee specification"""

    email: EmailStr


class GoogleCreateEventRequest(BaseModel):
    """
    Request model for creating a Google Calendar event.
    Corresponds to the request body of events.insert:
    https://developers.google.com/calendar/api/v3/reference/events/insert

    Note: calendar_id is passed as a path parameter (/calendars/{calendarId}/events),
    not in the request body
    """

    summary: str = Field(description="Title of the event")
    description: str | None = None
    location: str | None = None
    start: GoogleDateTime
    end: GoogleDateTime
    attendees: list[GoogleAttendee] | None = None


class GoogleLookupEventRequest(BaseModel):
    """
    Request model for listing Google Calendar events.
    Corresponds to the query parameters of events.list:
    https://developers.google.com/calendar/api/v3/reference/events/list

    Note: calendar_id is passed as a path parameter (/calendars/{calendarId}/events),
    not as a query parameter
    """

    timeMin: str = Field(description="RFC3339 lower bound for event time")
    timeMax: str = Field(description="RFC3339 upper bound for event time")
    timeZone: str = Field(description="IANA timezone for event times")
    q: str | None = Field(description="Free-text search across event fields")
    singleEvents: bool = Field(
        default=True, description="Expand recurring events into single instances"
    )
    orderBy: str = Field(default="startTime", description="Sort order of results")
    maxResults: int = Field(default=10, description="Maximum number of events to return")


def create_event_model_to_request(
    model: LlmCreateEvent,
) -> GoogleCreateEventRequest:
    """Convert LlmCreateEvent to GoogleCreateEventRequest"""
    return GoogleCreateEventRequest(
        summary=model.summary,
        description=model.description,
        location=model.location,
        start=GoogleDateTime(dateTime=model.start.dateTime, timeZone=model.start.timeZone),
        end=GoogleDateTime(dateTime=model.end.dateTime, timeZone=model.end.timeZone),
        attendees=[GoogleAttendee(email=att.email) for att in (model.attendees or [])] or None,
    )


def lookup_event_model_to_request(
    model: LlmEventLookup,
) -> GoogleLookupEventRequest:
    """
    Convert LlmEventLookup to GoogleLookupEventRequest.
    Used for searching events by time window and optional context terms.

    Note: For direct event ID lookups, use events.get instead of events.list
    """
    if not model.time_window:
        raise ValueError("Time window is required for event lookup")

    # Get the computed start and end times
    start = model.time_window.start
    end = model.time_window.end

    return GoogleLookupEventRequest(
        timeMin=start.dateTime,
        timeMax=end.dateTime,
        timeZone=model.time_window.center.timeZone,
        q=" ".join(model.context_terms) if model.context_terms else None,
    )
