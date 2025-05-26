"""
Create Event Extractor Module

Extractor node for event creation in the pipeline.
Extracts event details from event request using LLM call.
Pydantic response model is validated before passed to the next node in the pipeline.
"""

from typing import Any

from app.core.node import Node
from app.core.schema.task import TaskContext
from app.pipeline.schema.create import CreateContext, CreateResponse
from app.services.llm_factory import LLMFactory
from app.services.log_service import logger
from app.services.prompt_loader import PromptManager
from app.utils.datetime_utils import get_datetime_reference


class CreateEventExtractor(Node):
    """Extracts and normalizes details for event creation"""

    def __init__(self):
        """Initialize extractor with configuration"""
        self.llm = LLMFactory("openai")
        logger.info("Initialized %s", self.node_name)

    def get_context(self, task_context: TaskContext) -> CreateContext:
        """Extract context for event creation"""
        return CreateContext(
            request=task_context.event.request, datetime_ref=get_datetime_reference()
        )

    def create_completion(self, context: CreateContext) -> tuple[CreateResponse, Any]:
        """Extract and normalize event details using LLM with upfront datetime reference"""
        prompt = PromptManager.get_prompt(
            "create_event_extraction",
            datetime=context.datetime_ref.dateTime,
            timezone=context.datetime_ref.timeZone,
        )
        response_model, completion = self.llm.create_completion(
            response_model=CreateResponse,
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
        """Process event extraction and normalization"""
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
            logger.error("Extraction error: %s", str(e))
            task_context.nodes[self.node_name] = {"status": "error", "error": str(e)}

        return task_context

    def _log_results(self, response: CreateResponse):
        """Log extraction results"""
        logger.info("Extracted event details: '%s'", response.summary)
        if response.parsing_issues:
            logger.debug("Parsing issues: %s", ", ".join(response.parsing_issues))
        logger.debug("Extraction reasoning: %s", response.reasoning)
