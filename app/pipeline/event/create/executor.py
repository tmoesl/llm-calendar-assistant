"""
Create Event Executor Module

Execution node for event creation in the pipeline.
Handles the creation of calendar events using the Google Calendar API.
"""

from app.calendar.auth import GoogleAuthClient
from app.calendar.schema import create_event_model_to_request
from app.calendar.service import GoogleCalendarService
from app.core.node import Node
from app.core.schema.llm import LlmCreateEvent
from app.core.schema.task import TaskContext
from app.services.log_service import logger


class CreateEventExecutor(Node):
    """Creates events in Google Calendar using authenticated client."""

    def __init__(self):
        """Initialize with Google Calendar client."""
        self.client = GoogleAuthClient()
        logger.info("Initialized %s", self.node_name)

    def process(self, task_context: TaskContext) -> TaskContext:
        """Create event using extracted data."""
        try:
            # Get extracted event data
            extractor_result = task_context.nodes.get("CreateEventExtractor", {})
            if extractor_result.get("status") != "success":
                raise ValueError("Missing or failed event extraction")

            # Get validated event model
            event_model: LlmCreateEvent = extractor_result["response_model"]

            # Convert to Google API request model
            create_request = create_event_model_to_request(model=event_model)

            # Initialize calendar service
            service = self.client.authenticate()
            calendar_service = GoogleCalendarService(service)

            # Create the event
            created_event = calendar_service.create_event(
                calendar_id="primary",
                event_body=create_request.model_dump(exclude_none=True),
            )

            # Store result
            task_context.nodes[self.node_name] = {
                "status": "success",
                "response_model": created_event,
            }

            logger.info(
                "Created event: '%s' (id: %s)",
                created_event.get("summary", "Unknown"),
                created_event.get("id"),
            )

        except Exception as e:
            logger.error("Failed to create event: %s", str(e))
            task_context.nodes[self.node_name] = {"status": "error", "error": str(e)}

        return task_context
