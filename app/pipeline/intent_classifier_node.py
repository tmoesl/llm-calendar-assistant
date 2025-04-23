"""
Intent classification node for the pipeline.
Determines the type of calendar operation being requested.
"""

from app.llm.processor import classify_intent
from app.models.schemas import TaskEvent
from app.services.log_setup import logger

from .base_node import BaseNode


class IntentClassifierNode(BaseNode):
    """Classifies the intent of the calendar request"""

    def process(self, task: TaskEvent) -> TaskEvent:
        """
        Classify the intent of the user input

        Args:
            task: TaskEvent containing user input to classify

        Returns:
            TaskEvent with updated intent metadata and status
        """
        intent_result = classify_intent(task.user_input)

        task.metadata["intent"] = {
            "type": intent_result.request_type,
            "confidence": intent_result.confidence_score,
            "description": intent_result.description,
            "timestamp": task.timestamp,
        }

        logger.info(
            "Intent classified (type: %s, confidence: %.2f)",
            intent_result.request_type,
            intent_result.confidence_score,
        )

        task.status = "intent_classified"
        return task
