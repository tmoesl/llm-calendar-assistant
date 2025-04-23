"""
Router node for the pipeline.
Maps classified intents to their corresponding handlers.
"""

from app.handlers.event_handlers import get_handler_for_type
from app.models.schemas import TaskEvent
from app.services.log_setup import logger

from .base_node import BaseNode


class RouterNode(BaseNode):
    """Maps intents to their corresponding handlers"""

    def process(self, task: TaskEvent) -> TaskEvent:
        """
        Map the intent to appropriate handler

        Args:
            task: TaskEvent containing validated intent

        Returns:
            TaskEvent with handler mapping
        """
        intent_type = task.metadata["intent"]["type"]
        handler = get_handler_for_type(intent_type)

        task.metadata["routing"] = {
            "handler": handler.__name__ if handler else None,
            "intent_type": intent_type,
            "timestamp": task.timestamp,
        }

        if handler:
            logger.info(
                "Intent mapped to handler (type: %s, handler: %s)",
                intent_type,
                handler.__name__,
            )
            task.status = "routed"
        else:
            logger.warning("No handler found for intent (type: %s)", intent_type)
            task.status = "routing_failed"

        return task
