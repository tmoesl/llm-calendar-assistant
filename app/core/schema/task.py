"""
Task Context Schema Module

This module defines the Pydantic schema for the task context shared across pipeline nodes.
It provides type-safe structures for tracking pipeline state, intermediate results, metadata,
and error details throughout execution.
"""

from typing import Any

from pydantic import BaseModel, Field

from app.api.schema import EventSchema


class TaskContext(BaseModel):
    """Context container for calendar request processing.

    TaskContext maintains the state and results of a pipeline's execution,
    tracking the original event, intermediate node results, additional
    metadata and error handling throughout the processing flow.

    Attributes:
        event: The original event that triggered the pipeline
        nodes: Dictionary storing results and state from each node's execution
        metadata: Dictionary storing pipeline-level metadata and configuration
        error: Dictionary storing error information if pipeline execution fails

    Example:
        event = TaskContext(
            event=incoming_event,
            nodes={
                "ValidateInput": {
                    "response_model": response_model,
                    "usage": completion.usage,
                    "status": "success"
                }
            },
            metadata={},
            error=None
        )
    """

    event: EventSchema
    nodes: dict[str, Any] = Field(
        default_factory=dict,
        description="Results and status from each node's execution",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Pipeline configuration and metrics"
    )
    error: dict[str, Any] | None = Field(
        default=None,
        description="Error information if pipeline execution fails",
    )
