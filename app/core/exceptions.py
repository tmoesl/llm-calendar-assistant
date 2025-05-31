"""
Pipeline Exceptions and Error Messages

Defines exception hierarchy and standardized error message formatting
for the calendar assistant pipeline.
"""


class PipelineError(Exception):
    """Base exception for all pipeline-related errors."""

    pass


class CalServiceError(PipelineError):
    """Google Calendar API failures that might be transient and retryable."""

    pass


class LLMServiceError(PipelineError):
    """LLM service errors with potential retry logic."""

    pass


class ValidationError(PipelineError):
    """Data validation errors that are non-retryable."""

    pass


class ErrorMessages:
    """Standardized error message formatting utility."""

    @staticmethod
    def llm_failed(operation: str, error: str) -> str:
        return f"LLM {operation} failed: {error}"

    @staticmethod
    def calendar_failed(operation: str, error: str) -> str:
        return f"Google Calendar {operation} failed: {error}"

    @staticmethod
    def validation_failed(reason: str) -> str:
        return f"Validation failed: {reason}"
