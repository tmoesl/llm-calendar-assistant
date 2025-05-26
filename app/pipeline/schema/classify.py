"""
Classification Models Module

This module defines the models used for event classification.
"""

from pydantic import BaseModel, Field

from app.core.schema.event import EventType


class ClassifyContext(BaseModel):
    """Input context for intent classification"""

    request: str = Field(description="Original request body for the event")


class ClassifyResponse(BaseModel):
    """LLM response for intent classification"""

    # Intent classification
    has_intent: bool = Field(description="Whether a clear calendar intent was detected")
    request_type: EventType | None = Field(
        default=None, description="Classified intent type if clear intent detected"
    )
    is_bulk_operation: bool = Field(
        default=False, description="Whether the request is a bulk operation"
    )

    # Assessment details
    confidence_score: float = Field(
        ge=0.0, le=1.0, description="Confidence in intent classification"
    )
    reasoning: str = Field(description="Detailed explanation of classification results")
