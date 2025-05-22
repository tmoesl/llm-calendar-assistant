"""
Event Schema Module

This module defines the Pydantic models that FastAPI uses to validate incoming
HTTP requests. It specifies the expected structure and validation rules for
events entering the system through the API endpoints.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EventSchema(BaseModel):
    """Template for incoming event data."""

    request_id: UUID = Field(default_factory=uuid4, description="Unique identifier for the event")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Time when the event was created",
    )
    request: str = Field(..., min_length=1, description="The body of the event")
