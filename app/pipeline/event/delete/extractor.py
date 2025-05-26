"""
Delete Event Extractor Module

Extractor node for event deletion in the pipeline.
Extracts event details from event request using LLM call.
Pydantic response model is validated before passed to the next node in the pipeline.
"""

from typing import Any

from app.core.node import Node
from app.core.schema.task import TaskContext
from app.pipeline.schema.delete import DeleteContext, DeleteResponse
from app.services.llm_factory import LLMFactory
from app.services.log_service import logger
from app.services.prompt_loader import PromptManager
from app.utils.datetime_utils import get_datetime_reference


class DeleteEventExtractor(Node):
    """Extracts search criteria for event deletion"""

    def __init__(self):
        """Initialize extractor"""
        self.llm = LLMFactory("openai")
        logger.info("Initialized %s", self.node_name)

    def get_context(self, task_context: TaskContext) -> DeleteContext:
        """Extract context for deletion creation"""
        return DeleteContext(
            request=task_context.event.request,
            datetime_ref=get_datetime_reference(),
            is_bulk_operation=task_context.nodes["ClassifyEvent"][
                "response_model"
            ].is_bulk_operation,
        )

    def create_completion(self, context: DeleteContext) -> tuple[DeleteResponse, Any]:
        """Extract search criteria using LLM"""
        prompt = PromptManager.get_prompt(
            "delete_event_extraction",
            datetime=context.datetime_ref.dateTime,
            timezone=context.datetime_ref.timeZone,
            is_bulk_operation=context.is_bulk_operation,
        )
        response_model, completion = self.llm.create_completion(
            response_model=DeleteResponse,
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
        """Process deletion criteria extraction"""
        try:
            context = self.get_context(task_context)
            response_model, completion = self.create_completion(context)

            # Store results
            task_context.nodes[self.node_name] = {
                "response_model": response_model,
                "usage": completion.usage,
                "status": "success",
            }

            self._log_results(response_model)

        except Exception as e:
            logger.error("Failed to extract deletion criteria: %s", str(e))
            task_context.nodes[self.node_name] = {"status": "error", "error": str(e)}

        return task_context

    def _log_results(self, response: DeleteResponse):
        """Log extraction results"""
        # Log primary search criteria
        if response.event_id:
            logger.info("Extracted deletion criteria (event_id: %s)", response.event_id)
        else:
            logger.info(
                "Extracted deletion criteria (window: %s, context terms: %s)",
                response.time_window.original_reference if response.time_window else None,
                ", ".join(response.context_terms) if response.context_terms else None,
            )

        # Log any issues and reasoning
        if response.parsing_issues:
            logger.debug("Parsing issues: %s", ", ".join(response.parsing_issues))
        logger.debug("Extraction reasoning: %s", response.reasoning)
