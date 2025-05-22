"""
LLM Response Schema Module

This module defines the Pydantic models used to parse and validate responses from the LLM.
It specifies the type-safe structure for event fields, time windows, and search criteria,
and includes metadata for capturing parsing confidence, reasoning, and potential issues.
"""

from datetime import datetime, timedelta
from typing import Self
from zoneinfo import ZoneInfo, available_timezones

from dateutil.parser import isoparse
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    computed_field,
    field_validator,
    model_validator,
)

# ========================== BASE TIME MODELS ==========================
# Core models for handling time and timezone validation


class EventDateTime(BaseModel):
    """Event time specification with comprehensive validation"""

    dateTime: str = Field(description="RFC3339 timestamp with timezone offset")
    timeZone: str = Field(description="IANA timezone")

    @field_validator("dateTime")
    @classmethod
    def validate_datetime(cls, v: str) -> str:
        """Validate and parse ISO 8601 (RFC3339) datetime string"""
        try:
            dt = isoparse(v)
            if dt.tzinfo is None:
                raise ValueError("Datetime must include timezone offset")
            return v
        except Exception as exc:
            raise ValueError(
                f"Invalid RFC3339 dateTime string: {v}. Must be in format YYYY-MM-DDThh:mm:ss±hh:mm"
            ) from exc

    @field_validator("timeZone")
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        """Validate IANA timezone"""
        try:
            ZoneInfo(v)
            return v
        except Exception as exc:
            valid_zones = ", ".join(sorted(available_timezones())[:5]) + "..."
            raise ValueError(
                f"Invalid IANA timezone: {v}. Must be a valid IANA timezone (e.g., {valid_zones})"
            ) from exc

    @model_validator(mode="after")
    def validate_offset_matches_timezone(self) -> Self:
        """Ensure dateTime offset matches the IANA timeZone at that time"""
        try:
            dt = isoparse(self.dateTime)
            tz = ZoneInfo(self.timeZone)

            # Convert to the specified timezone
            dt_in_tz = dt.astimezone(tz)

            # Get the actual offset at that time (accounts for DST)
            actual_offset = dt.utcoffset()
            expected_offset = dt_in_tz.utcoffset()

            if actual_offset != expected_offset:
                raise ValueError(
                    f"DateTime offset ({actual_offset}) does not match "
                    f"timezone '{self.timeZone}' offset ({expected_offset}) "
                    f"at {self.dateTime}"
                )

            return self
        except Exception as exc:
            if not isinstance(exc, ValueError):
                raise ValueError(f"Failed to validate timezone offset: {str(exc)}") from exc
            raise

    def parsed_datetime(self) -> datetime:
        """Parse dateTime string into timezone-aware datetime object"""
        dt = isoparse(self.dateTime)
        return dt.astimezone(ZoneInfo(self.timeZone))


class TimeWindow(BaseModel):
    """Time window for event search"""

    center: EventDateTime = Field(description="Center of the time window")
    buffer_minutes: int = Field(default=5, description="Buffer time in minutes")
    original_reference: str = Field(description="Original reference for the time window")

    @computed_field
    def start(self) -> EventDateTime:
        """Start time of the time window"""
        center_dt = self.center.parsed_datetime()
        start_dt = center_dt - timedelta(minutes=self.buffer_minutes)
        return EventDateTime(
            dateTime=start_dt.isoformat(),
            timeZone=self.center.timeZone,
        )

    @computed_field
    def end(self) -> EventDateTime:
        """End time of the time window"""
        center_dt = self.center.parsed_datetime()
        end_dt = center_dt + timedelta(minutes=self.buffer_minutes)
        return EventDateTime(
            dateTime=end_dt.isoformat(),
            timeZone=self.center.timeZone,
        )

    @model_validator(mode="after")
    def validate_time_order(self) -> Self:
        """Ensure start < end"""
        start_dt = self.start.parsed_datetime()
        end_dt = self.end.parsed_datetime()
        if start_dt >= end_dt:
            raise ValueError("Start time must be before end time")
        return self


# ========================== BASE EVENT MODELS ==========================
# Core models for event fields and references


class EventReference(BaseModel):
    """Methods to identify an existing event"""

    event_id: str | None = Field(description="Google calendar event ID")
    time_window: TimeWindow | None = Field(description="Time window to search for the event")
    context_terms: list[str] = Field(
        default_factory=list, description="Keywords to identify the event"
    )

    @model_validator(mode="after")
    def validate_lookup_criteria(self) -> Self:
        """Ensure we have sufficient criteria to perform a lookup"""
        if not self.event_id and not (self.time_window and self.context_terms):
            raise ValueError(
                "Need either event_id or both time_window and context terms for lookup"
            )
        return self


class Attendee(BaseModel):
    """Event attendee"""

    email: EmailStr = Field(description="Email address")


class EventFields(BaseModel):
    """Common event fields"""

    summary: str | None = Field(description="Event title/summary")
    start: EventDateTime | None = Field(description="Event start time")
    end: EventDateTime | None = Field(description="Event end time")
    description: str | None = Field(description="Short statement of key topics/tasks")
    location: str | None = Field(description="Location of the event")
    attendees: list[Attendee] = Field(default_factory=list, description="List of attendees")

    @field_validator("summary", "description", "location", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str | None) -> str | None:
        """Strip whitespace from string fields"""
        if isinstance(v, str):
            return v.strip()
        return v

    @model_validator(mode="after")
    def validate_unique_attendees(self) -> Self:
        """Ensure all attendee emails are unique"""
        if not self.attendees:
            return self
        emails = [att.email.lower() for att in self.attendees]
        if len(set(emails)) != len(emails):
            raise ValueError("Duplicate attendee email addresses found")
        return self


# ========================== LLM OPERATION MODELS ==========================
# Models used for LLM-based operations, including parsing and validation metadata


class LlmCreateEvent(EventFields):
    """LLM model for event creation with required fields and parsing metadata"""

    # Required fields
    summary: str = Field(description="Event title/summary")
    start: EventDateTime = Field(description="Event start time")
    end: EventDateTime = Field(description="Event end time")

    # Debug metadata
    parsing_issues: list[str] = Field(default_factory=list)
    reasoning: str = Field(description="Explanation of extraction and normalization decisions")

    @model_validator(mode="after")
    def validate_event(self) -> Self:
        """Ensure start < end"""
        if self.start.parsed_datetime() >= self.end.parsed_datetime():
            raise ValueError("Start time must be before end time")
        return self

    model_config = {
        "json_schema_extra": {
            "example": {
                "summary": "Team Meeting",
                "start": {
                    "dateTime": "2025-05-07T10:00:00+10:00",
                    "timeZone": "Australia/Sydney",
                },
                "end": {
                    "dateTime": "2025-05-07T11:00:00+10:00",
                    "timeZone": "Australia/Sydney",
                },
                "description": "Monthly team sync",
                "location": "Conference Room A",
                "attendees": [
                    {"email": "alex@example.com"},
                    {"email": "john@example.com"},
                ],
                "parsing_issues": [],
                "reasoning": "Successfully extracted and normalized all fields. Used reference time to resolve 'tomorrow' to specific date.",
            }
        }
    }


class LlmDeleteEvent(EventReference):
    """LLM model for event deletion with parsing metadata"""

    # Debug metadata
    parsing_issues: list[str] = Field(default_factory=list)
    reasoning: str = Field(description="Explanation of extraction and normalization decisions")

    model_config = {
        "json_schema_extra": {
            "example": {
                "event_id": "abc123xyz789",  # Direct ID lookup
                "time_window": {  # Time-based lookup
                    "center": {
                        "dateTime": "2025-05-07T15:00:00+10:00",
                        "timeZone": "Australia/Sydney",
                    },
                    "buffer_minutes": 15,
                    "original_reference": "the meeting at 3pm",
                },
                "context_terms": ["team", "meeting", "monthly"],  # Search terms
                "parsing_issues": [],
                "reasoning": "Found event ID in user's reference. Also extracted time and context as fallback.",
            }
        }
    }


class LlmEventLookup(EventReference):
    """LLM model for looking up events using search criteria"""

    # Debug metadata
    parsing_issues: list[str] = Field(default_factory=list)
    reasoning: str = Field(description="Explanation of extraction and normalization decisions")


# computed_field: Exposes them in the model_dump() output without being part of the model's schema.
# model_validator: Validates the model as a whole, allowing for cross-field validation.
# field_validator: Validates individual fields, allowing for custom validation logic.
# property: Standard Python property, used for computed attributes that are not part of the model's schema.
