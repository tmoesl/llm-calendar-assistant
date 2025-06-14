"""
Validation Module

Node for event request validation in the pipeline.
Validates security and legitimacy of calendar requests.
"""

from typing import Any

from app.config.settings import get_settings
from app.core.exceptions import ErrorMessages, LLMServiceError, ValidationError
from app.core.node import Node
from app.core.schema.task import TaskContext
from app.llm.factory import LLMFactory
from app.logging.factory import logger
from app.pipeline.schema.validate import ValidateContext, ValidateResponse
from app.services.prompt_loader import PromptManager


class ValidateEvent(Node):
    """Validates the event request for legitimacy and safety."""

    def __init__(self):
        """Initialize validator"""
        settings = get_settings()
        self.confidence_threshold = settings.llm.confidence_threshold
        self.llm_provider = LLMFactory("openai")
        logger.info("Initialized %s", self.node_name)

    def get_context(self, task_context: TaskContext) -> ValidateContext:
        """Extract context for validation"""
        return ValidateContext(request=task_context.event.request)

    def create_completion(self, context: ValidateContext) -> tuple[ValidateResponse, Any]:
        """Get validation results from LLM"""
        prompt = PromptManager.get_prompt("validate_event_request")
        response_model, completion = self.llm_provider.create_completion(
            response_model=ValidateResponse,
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
        """Process combined validation"""
        context = self.get_context(task_context)

        try:
            response_model, completion = self.create_completion(context)
        except Exception as llm_error:
            raise LLMServiceError(
                ErrorMessages.llm_failed("validation", str(llm_error))
            ) from llm_error

        # Event validation logic
        is_valid = (
            response_model.is_safe
            and response_model.is_valid
            and response_model.confidence_score >= self.confidence_threshold
        )

        if not is_valid:
            raise ValidationError(ErrorMessages.validation_failed(response_model.reasoning))

        # Store result
        task_context.update_node(
            self.node_name,
            response_model=response_model,
            usage=completion.usage,
        )

        self._log_validation_results(is_valid, response_model)

        return task_context

    def _log_validation_results(self, is_valid: bool, response_model: ValidateResponse):
        """Log validation results with summary and optional details"""
        if is_valid:
            logger.info("Validation passed (confidence: %.2f)", response_model.confidence_score)
            return

        # Collect failed validation types
        failures = []
        if not response_model.is_safe:
            failures.append("security risk")
        if not response_model.is_valid:
            failures.append("invalid request")
        if response_model.confidence_score < self.confidence_threshold:
            failures.append("low confidence")

        # Log summary at INFO level
        logger.info("Validation failed (%s)", ", ".join(failures))

        # Log details at DEBUG level
        if not response_model.is_safe:
            logger.debug("Security details: %s", ", ".join(response_model.risk_flags))
        if not response_model.is_valid:
            logger.debug("Validity details: %s", response_model.invalid_reason)
        if response_model.confidence_score < self.confidence_threshold:
            logger.debug(
                "Confidence details: %.2f < %.2f",
                response_model.confidence_score,
                self.confidence_threshold,
            )
