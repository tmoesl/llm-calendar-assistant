"""
Event Lookup Models Module

This module defines the models used for event lookup and extraction.
"""

from pydantic import BaseModel, Field

from app.core.schema.event import EventDateTime, EventLookup


class LookupContext(BaseModel):
    """Input context for event lookup extraction"""

    request: str = Field(description="Original request body for the event")
    datetime_ref: EventDateTime = Field(description="Current datetime and timezone reference")
    is_bulk_operation: bool = Field(
        default=False, description="Whether the request is a bulk operation"
    )


class LookupResponse(EventLookup):
    """LLM response for event lookup extraction with parsing metadata"""

    # Debug metadata
    parsing_issues: list[str] = Field(default_factory=list)
    reasoning: str = Field(description="Explanation of extraction and normalization decisions")
