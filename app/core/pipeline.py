"""
Pipeline Module

This module implements the core pipeline functionality.
It provides a flexible way to execute a series of nodes in sequence,
with support for routing logic, logging, and error handling.
"""

from abc import ABC
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import ClassVar

from app.api.schema import EventSchema
from app.core.node import Node
from app.core.router import Router
from app.core.schema.pipeline import NodeConfig, PipelineSchema
from app.core.schema.task import TaskContext
from app.services.log_service import logger


class Pipeline(ABC):
    """Abstract base class for defining processing pipelines.

    The Pipeline class provides a framework for creating processing pipelines
    with multiple nodes and routing logic. Each pipeline must define its structure
    using a PipelineSchema.

    Attributes:
        pipeline_schema: Class variable defining the pipeline's structure and flow
        nodes: Dictionary mapping node classes to their instances
    """

    pipeline_schema: ClassVar[PipelineSchema]

    def __init__(self):
        """Initializes pipeline nodes"""
        self.nodes: dict[type[Node], NodeConfig] = {}
        self._initialize_nodes()

    def _initialize_nodes(self) -> None:
        """Initializes all nodes based on the pipeline schema."""

        for node_config in self.pipeline_schema.nodes:
            # Add the explicitly defined node to the dict
            self.nodes[node_config.node] = node_config

            for connected_node in node_config.connections:
                # If a connected node isn't declared yet, add it
                if connected_node not in self.nodes:
                    self.nodes[connected_node] = NodeConfig(node=connected_node)

    @contextmanager
    def node_context(self, node_name: str):
        """Context manager for logging node execution and handling errors.

        Args:
            node_name: Name of the node being executed

        Yields:
            None

        Raises:
            Exception: Re-raises any exception that occurs during node execution
        """
        logger.info(f"Starting node: {node_name}")
        try:
            yield
        except Exception as e:
            logger.error(f"Error in node {node_name}: {str(e)}")
            raise
        finally:
            logger.info(f"Completed node: {node_name}")

    def run(self, event: EventSchema) -> TaskContext:
        """Executes the pipeline for a given event.

        Args:
            event: The event to process through the pipeline

        Returns:
            TaskContext containing the results of pipeline execution

        Raises:
            Exception: Any exception that occurs during pipeline execution
        """
        task_context = TaskContext(event=event)
        task_context.metadata["nodes"] = self.nodes
        current_node_class = self.pipeline_schema.start

        try:
            while current_node_class:
                current_node = self.nodes[current_node_class].node()  # Instantiate the node
                with self.node_context(current_node_class.__name__):
                    task_context = current_node.process(task_context)

                current_node_class = self._get_next_node_class(current_node_class, task_context)

        except Exception as pipeline_error:
            logger.error("Pipeline error: %s", str(pipeline_error))
            task_context.error = {
                "type": "pipeline_error",
                "message": str(pipeline_error),
                "node": current_node_class.__name__ if current_node_class else None,
                "timestamp": datetime.now(UTC).isoformat(),
            }

        task_context.metadata.pop(
            "nodes", None
        )  # Remove nodes from metadata to avoid circular references, serialization issues and security risks
        return task_context

    def _get_next_node_class(
        self, current_node_class: type[Node], task_context: TaskContext
    ) -> type[Node] | None:
        """Determines the next node to execute in the pipeline.

        Args:
            current_node_class: The class of the current node
            task_context: The current task context

        Returns:
            The class of the next node to execute, or None if at the end
        """
        # Check node status
        node_name = current_node_class.__name__
        node_status = task_context.nodes.get(node_name, {}).get("status", "")
        if node_status in ["failed", "blocked", "error"]:
            return None

        node_config = self.nodes.get(current_node_class)
        if not node_config or not node_config.connections:
            return None

        if node_config.is_router:
            router: Router = node_config.node()  # type: ignore # Instantiate the router
            return self._handle_router(router, task_context)

        return node_config.connections[0]

    def _handle_router(self, router: Router, task_context: TaskContext) -> type[Node] | None:
        """Handles routing logic for router nodes.

        Args:
            router: The router node instance
            task_context: The current task context

        Returns:
            The class of the next node to execute, or None if at the end
        """
        return router.route(task_context)
