"""
Classification Module

Node for event classification in the pipeline.
Classifies the type of event requested.
"""

from typing import Any

from app.config.settings import get_settings
from app.core.node import Node
from app.core.schema.task import TaskContext
from app.pipeline.schema.classify import ClassifyContext, ClassifyResponse
from app.services.llm_factory import LLMFactory
from app.services.log_service import logger
from app.services.prompt_loader import PromptManager


class ClassifyEvent(Node):
    """Classifies the type of calendar event requested"""

    def __init__(self):
        """Initialize classifier with configuration"""
        settings = get_settings()
        self.confidence_threshold = settings.app.confidence_threshold
        self.llm = LLMFactory("openai")
        logger.info("Initialized %s", self.node_name)

    def get_context(self, task_context: TaskContext) -> ClassifyContext:
        """Extract context for intent classification"""
        return ClassifyContext(request=task_context.event.request)

    def create_completion(self, context: ClassifyContext) -> tuple[ClassifyResponse, Any]:
        """Get validation results from LLM"""
        prompt = PromptManager.get_prompt("classify_event_request")
        response_model, completion = self.llm.create_completion(
            response_model=ClassifyResponse,
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                },
                {
                    "role": "user",
                    "content": context.request,
                },
            ],
        )
        return response_model, completion

    def process(self, task_context: TaskContext) -> TaskContext:
        """Process intent classification"""
        try:
            context = self.get_context(task_context)
            response_model, completion = self.create_completion(context)

            # Core validation check
            is_classified = (
                response_model.has_intent
                and response_model.request_type is not None
                and response_model.confidence_score >= self.confidence_threshold
            )

            # Store results
            task_context.nodes[self.node_name] = {
                "response_model": response_model,
                "usage": completion.usage,
                "status": "blocked" if not is_classified else "success",
                "details": {
                    "has_intent": response_model.has_intent,
                    "intent_type": response_model.request_type,
                    "confidence": response_model.confidence_score,
                    "reasoning": response_model.reasoning,
                },
            }

            self._log_classification_results(is_classified, response_model)

        except Exception as e:
            logger.error("Unexpected error in validation: %s", str(e))
            task_context.nodes[self.node_name] = {"status": "error", "error": str(e)}

        return task_context

    def _log_classification_results(self, is_valid: bool, response: ClassifyResponse):
        """Log classification results with summary and details"""
        if is_valid:
            logger.info(
                "Intent classified as '%s' (confidence: %.2f)",
                response.request_type.value if response.request_type else None,
                response.confidence_score,
            )
            return

        # Collect failed classification types
        failures = []
        if not response.has_intent:
            failures.append("invalid intent")
        if response.confidence_score < self.confidence_threshold:
            failures.append("low confidence")

        # Log summary at INFO level
        logger.info("Classification failed (%s)", ", ".join(failures))

        # Log details at DEBUG level
        logger.debug(
            "Classification details: %s (confidence: %.2f)",
            response.reasoning,
            response.confidence_score,
        )
