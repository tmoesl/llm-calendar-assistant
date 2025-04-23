from datetime import datetime, timezone
from typing import Any, Dict, Literal, Optional
from uuid import uuid4

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


class EventDetails(BaseModel):
    """Core event details for calendar operations"""

    title: str = Field(description="Title of the calendar event")
    start_time: datetime = Field(description="Event start time")
    end_time: datetime = Field(description="Event end time")
    description: Optional[str] = Field(None, description="Description of the event")
    location: Optional[str] = Field(None, description="Event location")
    attendees: list[str] = Field(
        default_factory=list, description="List of attendee emails"
    )
    timezone: str = Field(default="UTC", description="Timezone for the event")


class TaskEvent(BaseModel):
    """Pipeline task event that tracks calendar request processing"""

    request_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for this calendar request",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this request was created",
    )
    status: str = Field(
        default="initialized", description="Current status of the request"
    )
    event_details: Optional[EventDetails] = Field(
        default=None, description="Calendar event details once extracted"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Metadata from pipeline processing steps"
    )
