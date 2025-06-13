"""
Classification Module

Node for event classification in the pipeline.
Classifies the type of event requested.
"""

from typing import Any

from app.config.settings import get_settings
from app.core.exceptions import ErrorMessages, LLMServiceError, ValidationError
from app.core.node import Node
from app.core.schema.task import TaskContext
from app.pipeline.schema.classify import ClassifyContext, ClassifyResponse
from app.services.llm_factory import LLMFactory
from app.services.logger_factory import logger
from app.services.prompt_loader import PromptManager


class ClassifyEvent(Node):
    """Classifies the type of calendar event requested"""

    def __init__(self):
        """Initialize classifier"""
        settings = get_settings()
        self.confidence_threshold = settings.llm.confidence_threshold
        self.llm_provider = LLMFactory("openai")
        logger.info("Initialized %s", self.node_name)

    def get_context(self, task_context: TaskContext) -> ClassifyContext:
        """Extract context for intent classification"""
        return ClassifyContext(request=task_context.event.request)

    def create_completion(self, context: ClassifyContext) -> tuple[ClassifyResponse, Any]:
        """Get validation results from LLM"""
        prompt = PromptManager.get_prompt("classify_event_request")
        response_model, completion = self.llm_provider.create_completion(
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
        context = self.get_context(task_context)

        try:
            response_model, completion = self.create_completion(context)
        except Exception as llm_error:
            raise LLMServiceError(
                ErrorMessages.llm_failed("classification", str(llm_error))
            ) from llm_error

        # Event classification logic
        is_classified = (
            response_model.has_intent
            and response_model.request_type is not None
            and response_model.confidence_score >= self.confidence_threshold
        )

        if not is_classified:
            raise ValidationError(ErrorMessages.validation_failed(response_model.reasoning))

        # Store result
        task_context.update_node(
            self.node_name,
            response_model=response_model,
            usage=completion.usage,
        )

        self._log_classification_results(is_classified, response_model)

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
