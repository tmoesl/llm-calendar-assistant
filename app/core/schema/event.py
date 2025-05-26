"""
Core Event Models Module

This module defines the core event models used across the application.
It provides base models for event datetime handling, time windows, and common event fields.
These models are independent of specific operations (create, delete, etc).
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Self
from zoneinfo import ZoneInfo, available_timezones

from dateutil.parser import isoparse
from pydantic import BaseModel, EmailStr, Field, computed_field, field_validator, model_validator


class EventType(str, Enum):
    """Enum for event types"""

    CREATE_EVENT = "create_event"
    UPDATE_EVENT = "update_event"
    DELETE_EVENT = "delete_event"
    VIEW_EVENT = "view_event"


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
            dt_in_tz = dt.astimezone(tz)
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


class EventTimeWindow(BaseModel):
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


class EventLookup(BaseModel):
    """Base model for event lookup operations with search criteria"""

    event_id: str | None = Field(description="Google calendar event ID")
    time_window: EventTimeWindow | None = Field(description="Time window to search for the event")
    context_terms: list[str] = Field(
        default_factory=list, description="Keywords to identify the event"
    )

    @model_validator(mode="after")
    def validate_lookup_criteria(self) -> Self:
        """Ensure we have sufficient criteria to perform a lookup"""
        if not self.event_id and not self.time_window:
            raise ValueError("Need either event_id or time_window for lookup")
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

    @model_validator(mode="after")
    def validate_event_times(self) -> Self:
        """Ensure start < end if both are provided"""
        if self.start and self.end and self.start.parsed_datetime() >= self.end.parsed_datetime():
            raise ValueError("Start time must be before end time")
        return self


# computed_field: Exposes them in the model_dump() output without being part of the model's schema.
# model_validator: Validates the model as a whole, allowing for cross-field validation.
# field_validator: Validates individual fields, allowing for custom validation logic.
# property: Standard Python property, used for computed attributes that are not part of the model's schema.
