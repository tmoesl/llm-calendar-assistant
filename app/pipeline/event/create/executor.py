"""
Create Event Executor Module

Execution node for event creation in the pipeline.
Handles the creation of calendar events using the Google Calendar API.
"""

from app.calendar.auth import GoogleAuthClient
from app.calendar.schema import GoogleEventResponse, create_event_model_to_request
from app.calendar.service import GoogleCalendarService
from app.config.settings import get_settings
from app.core.exceptions import CalServiceError, ErrorMessages, ValidationError
from app.core.node import Node
from app.core.schema.task import TaskContext
from app.services.logger_factory import logger


class CreateEventExecutor(Node):
    """Creates events in Google Calendar using authenticated client."""

    def __init__(self):
        """Initialize with Google Calendar client."""
        settings = get_settings()
        self.client = GoogleAuthClient()
        self.calendar_id = settings.app.calendar_id
        logger.info("Initialized %s", self.node_name)

    def process(self, task_context: TaskContext) -> TaskContext:
        """Create event using extracted data."""
        # Get extracted event data
        extractor_result = task_context.nodes.get("CreateEventExtractor", {})
        if not extractor_result or "response_model" not in extractor_result:
            raise ValidationError(
                ErrorMessages.validation_failed("event details could not be extracted from request")
            )

        # Get validated event model
        event_model = extractor_result["response_model"]

        # Convert to Google API request model
        create_request = create_event_model_to_request(model=event_model)

        # Initialize calendar service
        service = self.client.authenticate()
        calendar_service = GoogleCalendarService(service)

        try:
            # Create the event
            created_event_raw = calendar_service.create_event(
                calendar_id=self.calendar_id,
                event_body=create_request.model_dump(exclude_none=True),
            )
        except Exception as api_error:
            raise CalServiceError(
                ErrorMessages.calendar_failed("event creation", str(api_error))
            ) from api_error

        # Validate response with schema
        created_event = GoogleEventResponse(**created_event_raw)

        # Store result
        task_context.update_node(
            self.node_name,
            response_model=created_event,
        )

        logger.info("Created 1 event in calendar")

        return task_context
