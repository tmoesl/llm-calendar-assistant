"""
Routing Module

Routing Node for event routing in the pipeline.
Routes events based on event type classification.
"""

from app.core.node import Node
from app.core.router import Router, RouterNode
from app.core.schema.event import EventType
from app.core.schema.task import TaskContext
from app.pipeline.event.create.extractor import CreateEventExtractor
from app.pipeline.event.delete.extractor import DeleteEventExtractor


class RouteEvent(Router):
    """Routes based on event type classification"""

    def __init__(self):
        super().__init__()
        self.routes = [CreateEventRouter, DeleteEventRouter]  # classes not instantiated
        self.fallback = None


class CreateEventRouter(RouterNode):
    """Routes create event to appropriate extractor"""

    def determine_next_node(self, task_context: TaskContext) -> type[Node] | None:
        classification = task_context.nodes["ClassifyEvent"]["response_model"]
        if classification.request_type == EventType.CREATE_EVENT:
            return CreateEventExtractor
        return None


class DeleteEventRouter(RouterNode):
    """Routes delete event to appropriate extractor"""

    def determine_next_node(self, task_context: TaskContext) -> type[Node] | None:
        classification = task_context.nodes["ClassifyEvent"]["response_model"]
        if classification.request_type == EventType.DELETE_EVENT:
            return DeleteEventExtractor
        return None
