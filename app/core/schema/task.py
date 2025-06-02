"""
Task Context Schema Module

This module defines the Pydantic schema for the task context shared across pipeline nodes.
It provides type-safe structures for tracking pipeline state, intermediate results, and metadata
throughout execution.
"""

from typing import Any

from pydantic import BaseModel, Field

from app.api.schema import EventSchema


class TaskContext(BaseModel):
    """Context container for calendar request processing.

    TaskContext maintains the state and results of a pipeline's execution,
    tracking the original event, intermediate node results, and additional
    metadata throughout the processing flow.

    Attributes:
        event: The original event that triggered the pipeline
        nodes: Dictionary storing results and state from each node's execution
        metadata: Dictionary storing pipeline-level metadata and configuration

    Example:
        task_context = TaskContext(
            event=incoming_event,
            nodes={
                "ValidateEvent": {
                    "response_model": response_model,
                    "usage": completion.usage
                }
            },
            metadata={}
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

    def update_node(self, node_name: str, **kwargs: Any) -> None:
        """Update node data with new key-value pairs using safe dictionary merging.

        This method provides a clean interface for updating node execution results
        while preserving existing data. It safely merges new data with existing
        node data, creating the node entry if it doesn't exist.

        Args:
            node_name: The name of the node to update
            **kwargs: Key-value pairs to merge into the node's data

        Note:
            Uses dictionary unpacking for safe merging: {**existing, **new}
            If the node doesn't exist, creates a new entry with the provided data.

        Example:
            task_context.update_node("ClassifyEvent",
                        response_model=response_model,
                        usage=completion.usage,
                        details={
                            "intent_type": "CREATE_EVENT",
                            "confidence": 0.95,
                        },
                    )
        """
        self.nodes[node_name] = {**self.nodes.get(node_name, {}), **kwargs}
