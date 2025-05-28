"""
Validation Module

Node for event request validation in the pipeline.
Validates security and legitimacy of calendar requests.
"""

from typing import Any

from app.config.settings import get_settings
from app.core.node import Node
from app.core.schema.task import TaskContext
from app.pipeline.schema.validate import ValidateContext, ValidateResponse
from app.services.llm_factory import LLMFactory
from app.services.log_service import logger
from app.services.prompt_loader import PromptManager


class ValidateEvent(Node):
    """Validates the event request for legitimacy and safety."""

    def __init__(self):
        """Initialize validator with configuration"""
        settings = get_settings()
        self.confidence_threshold = settings.app.confidence_threshold
        self.llm = LLMFactory("openai")
        logger.info("Initialized %s", self.node_name)

    def get_context(self, task_context: TaskContext) -> ValidateContext:
        """Extract context for validation"""
        return ValidateContext(request=task_context.event.request)

    def create_completion(self, context: ValidateContext) -> tuple[ValidateResponse, Any]:
        """Get validation results from LLM"""
        prompt = PromptManager.get_prompt("validate_event_request")
        response_model, completion = self.llm.create_completion(
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
        try:
            context = self.get_context(task_context)
            response_model, completion = self.create_completion(context)

            # Check both validations
            is_valid = (
                response_model.is_safe
                and response_model.is_valid
                and response_model.confidence_score >= self.confidence_threshold
            )

            # Store results
            task_context.nodes[self.node_name] = {
                "response_model": response_model,
                "usage": completion.usage,
                "status": "success" if is_valid else "blocked",
            }

            self._log_validation_results(is_valid, response_model)

        except Exception as e:
            logger.error("Validation error: %s", str(e))
            task_context.nodes[self.node_name] = {"status": "error", "error": str(e)}

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
