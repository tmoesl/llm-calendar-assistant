"""
Create Event Models Module

This module defines the models used for event creation.
"""

from pydantic import BaseModel, Field

from app.core.schema.event import AllDayEventDate, EventDateTime, EventFields


class CreateContext(BaseModel):
    """Input context for event creation"""

    request: str = Field(description="Original request body for the event")
    datetime_ref: EventDateTime = Field(description="Current datetime and timezone reference")


class CreateResponse(EventFields):
    """LLM response for event creation with required fields and parsing metadata"""

    # Required fields
    summary: str = Field(description="Event title/summary")
    start: EventDateTime | AllDayEventDate = Field(description="Event start time or date")
    end: EventDateTime | AllDayEventDate = Field(description="Event end time or date")

    # Debug metadata
    parsing_issues: list[str] = Field(default_factory=list)
    reasoning: str = Field(description="Explanation of extraction and normalization decisions")
