"""
Router Module

This module implements the routing logic for pipeline nodes.
It provides base classes for implementing routing decisions between nodes
in a processing pipeline.
"""

from abc import ABC, abstractmethod

from app.core.node import Node
from app.core.schema.task import TaskContext


class RouterNode(ABC):
    """Base interface for router condition nodes"""

    @abstractmethod
    def determine_next_node(self, task_context: TaskContext) -> type[Node] | None:
        """Determine the next node based on the routing rules"""
        pass

    @property
    def node_name(self):
        """Returns the name of the node"""
        return self.__class__.__name__


class Router(Node):
    """Base router implementation that manages multiple routing rules.

    The Router class provides core routing functionality for directing
    task flow between pipeline nodes. It processes routing rules in sequence
    and falls back to a default node if no rules match.

    Attributes:
        routes: List of RouterNode classes defining routing rules
        fallback: Optional default node to route to if no rules match
    """

    def __init__(self):
        self.routes: list[type[RouterNode]] = []  # Router classes
        self.fallback: type[Node] | None = None  # Node class

    def process(self, task_context: TaskContext) -> TaskContext:
        """Processes the routing logic and updates task context.

        Args:
            task_context: Current task execution context

        Returns:
            Updated TaskContext with routing decision recorded
        """
        next_node_class = self.route(task_context)
        task_context.nodes[self.node_name] = {
            "next_node": next_node_class.__name__ if next_node_class else None,
        }
        return task_context

    def route(self, task_context: TaskContext) -> type[Node] | None:
        """Determines the next node based on routing rules.

        Evaluates each routing rule in sequence and returns the first
        matching node. Falls back to the default node if no rules match.

        Args:
            task_context: Current task execution context

        Returns:
            The next node to execute, or None if no route is found
        """
        for router_class in self.routes:
            router = router_class()  # Instantiate the router instance
            next_node_class = router.determine_next_node(task_context)
            if next_node_class:
                return next_node_class
        return self.fallback
