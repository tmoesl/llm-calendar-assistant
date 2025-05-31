"""
Event Lookup Extractor Module

Extractor node for event lookup in the pipeline.
Extracts event details from event request using LLM call.
Pydantic response model is validated before passed to the next node in the pipeline.
"""

from typing import Any

from app.core.exceptions import ErrorMessages, LLMServiceError
from app.core.node import Node
from app.core.schema.task import TaskContext
from app.pipeline.schema.lookup import LookupContext, LookupResponse
from app.services.llm_factory import LLMFactory
from app.services.log_service import logger
from app.services.prompt_loader import PromptManager
from app.utils.datetime_utils import get_datetime_reference


class LookupEventExtractor(Node):
    """Extracts search criteria for event lookup"""

    def __init__(self):
        """Initialize extractor"""
        self.llm = LLMFactory("openai")
        logger.info("Initialized %s", self.node_name)

    def get_context(self, task_context: TaskContext) -> LookupContext:
        """Extract context for lookup criteria extraction"""
        return LookupContext(
            request=task_context.event.request,
            datetime_ref=get_datetime_reference(),
            is_bulk_operation=task_context.nodes["ClassifyEvent"][
                "response_model"
            ].is_bulk_operation,
        )

    def create_completion(self, context: LookupContext) -> tuple[LookupResponse, Any]:
        """Extract search criteria using LLM"""
        prompt = PromptManager.get_prompt(
            "lookup_event_extraction",
            datetime=context.datetime_ref.dateTime,
            timezone=context.datetime_ref.timeZone,
            is_bulk_operation=context.is_bulk_operation,
        )
        response_model, completion = self.llm.create_completion(
            response_model=LookupResponse,
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
        """Process lookup criteria extraction"""
        context = self.get_context(task_context)

        try:
            response_model, completion = self.create_completion(context)
        except Exception as llm_error:
            raise LLMServiceError(
                ErrorMessages.llm_failed("lookup extraction", str(llm_error))
            ) from llm_error

        # Store result
        task_context.nodes[self.node_name] = {
            "response_model": response_model,
            "usage": completion.usage,
        }

        self._log_results(response_model)

        return task_context

    def _log_results(self, response: LookupResponse):
        """Log extraction results"""
        # Log primary search criteria
        if response.event_id:
            logger.info("Extracted lookup criteria (event_id: %s)", response.event_id)
        else:
            logger.info(
                "Extracted lookup criteria (window: %s, context terms: %s)",
                response.time_window.original_reference if response.time_window else None,
                ", ".join(response.context_terms) if response.context_terms else None,
            )

        # Log any issues and reasoning
        if response.parsing_issues:
            logger.debug("Parsing issues: %s", ", ".join(response.parsing_issues))
        logger.debug("Extraction reasoning: %s", response.reasoning)
