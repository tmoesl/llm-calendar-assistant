"""
Lookup event node for the pipeline.
Handles the retrieval of calendar events.
"""

from app.calendar.auth import GoogleAuthClient
from app.calendar.config import get_calendar_config
from app.calendar.schema import (
    GoogleEventResponse,
    GoogleLookupEventResponse,
    lookup_event_model_to_request,
)
from app.calendar.service import GoogleCalendarService
from app.core.exceptions import CalServiceError, ErrorMessages, ValidationError
from app.core.node import Node
from app.core.schema.task import TaskContext
from app.logging.factory import logger


class LookupEventExecutor(Node):
    """Node to execute event lookup based on extracted details."""

    def __init__(self):
        """Initialize with Google Calendar client."""
        config = get_calendar_config()
        self.client = GoogleAuthClient()
        self.calendar_id = config.calendar_id
        logger.info("Initialized %s", self.node_name)

    def process(self, task_context: TaskContext) -> TaskContext:
        """Look up events using search criteria."""
        # Get extracted event search parameters
        extractor_result = task_context.nodes.get("LookupEventExtractor", {})
        if not extractor_result or "response_model" not in extractor_result:
            raise ValidationError(
                ErrorMessages.validation_failed(
                    "event search criteria could not be extracted from request"
                )
            )

        # Get validated event search parameters
        search_params = extractor_result["response_model"]

        try:
            # Initialize calendar service
            service = self.client.authenticate()
            calendar_service = GoogleCalendarService(service)

            # Find matching events
            if search_params.event_id:
                # Direct event ID lookup using events.get
                event_raw = calendar_service.get_event(
                    calendar_id=self.calendar_id, event_id=search_params.event_id
                )
                events_raw = [event_raw] if event_raw else []
            else:
                # Search by criteria using events.list
                if not search_params.time_window:
                    raise ValidationError(
                        ErrorMessages.validation_failed(
                            "event search criteria not valid - time period required"
                        )
                    )

                lookup_request = lookup_event_model_to_request(model=search_params)
                events_raw = calendar_service.list_events(
                    calendar_id=self.calendar_id,
                    **lookup_request.model_dump(exclude_none=True),
                )
        except Exception as e:
            raise CalServiceError(ErrorMessages.calendar_failed("event lookup", str(e))) from e

        # Validate each event with schema
        validated_events = [GoogleEventResponse(**event) for event in events_raw if event]

        # Create lookup response
        found_events = GoogleLookupEventResponse(items=validated_events)

        # Validate results
        if not found_events.items:
            raise ValidationError(
                ErrorMessages.validation_failed("event lookup did not find any matching events")
            )

        # Store result
        task_context.update_node(
            self.node_name,
            response_model=found_events,
        )

        logger.info(
            "Found %d event%s in calendar",
            len(found_events.items),
            "" if len(found_events.items) == 1 else "s",
        )

        return task_context
