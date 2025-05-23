"""
Delete Event Models Module

This module defines the models used for event deletion.
"""

from pydantic import BaseModel, Field

from app.core.schema.event import EventDateTime, EventLookup


class DeleteContext(BaseModel):
    """Input context for event deletion"""

    request: str = Field(description="Original request body for the event")
    datetime_ref: EventDateTime = Field(description="Current datetime and timezone reference")


class DeleteResponse(EventLookup):
    """LLM response for event deletion with parsing metadata"""

    # Debug metadata
    parsing_issues: list[str] = Field(default_factory=list)
    reasoning: str = Field(description="Explanation of extraction and normalization decisions")
