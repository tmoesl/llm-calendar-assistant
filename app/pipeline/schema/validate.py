"""
Validation Models Module

This module defines the models used for event validation.
"""

from pydantic import BaseModel, Field


class ValidateContext(BaseModel):
    """Context for event validation"""

    request: str = Field(description="Original request body for the event")


class ValidateResponse(BaseModel):
    """Response model for security check"""

    # Security validation
    is_safe: bool = Field(description="Whether the input is considered safe")
    risk_flags: list[str] = Field(description="List of identified security risks")

    # Calendar request validation
    is_valid: bool = Field(description="Whether the input is legitimate calendar request")
    invalid_reason: str = Field(
        description="Reason why request is not calendar-related if applicable"
    )

    # Combined validation score
    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in calender validation and security assessment",
    )
    reasoning: str = Field(description="Detailed explanation of validation results")
