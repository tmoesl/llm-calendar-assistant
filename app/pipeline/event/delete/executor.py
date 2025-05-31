"""
Delete Event Executor Module

Execution node for event deletion in the pipeline.
Handles the deletion of calendar events using the Google Calendar API.
"""

from app.calendar.auth import GoogleAuthClient
from app.calendar.schema import GoogleLookupEventResponse
from app.calendar.service import GoogleCalendarService
from app.core.exceptions import CalServiceError, ErrorMessages, ValidationError
from app.core.node import Node
from app.core.schema.task import TaskContext
from app.services.log_service import logger


class DeleteEventExecutor(Node):
    """Deletes events from Google Calendar using search criteria."""

    def __init__(self):
        """Initialize with Google Calendar client."""
        self.client = GoogleAuthClient()
        logger.info("Initialized %s", self.node_name)

    def process(self, task_context: TaskContext) -> TaskContext:
        """Delete events using lookup results."""
        # Get event lookup results
        lookup_result = task_context.nodes.get("LookupEventExecutor", {})
        if not lookup_result or "response_model" not in lookup_result:
            raise ValidationError(
                ErrorMessages.validation_failed(
                    "target events for deletion could not be identified"
                )
            )

        # Get validated events to delete
        found_events = lookup_result["response_model"]

        # Initialize calendar service
        service = self.client.authenticate()
        calendar_service = GoogleCalendarService(service)

        # Delete all found events
        deleted_events = GoogleLookupEventResponse(items=[])

        for event in found_events.items:
            try:
                # Delete the event
                calendar_service.delete_event(
                    calendar_id="primary",
                    event=event,
                    sendUpdates="none",  # Default to no notifications
                )
                deleted_events.items.append(event)
            except Exception as api_error:
                raise CalServiceError(
                    ErrorMessages.calendar_failed("event deletion", str(api_error))
                ) from api_error

        # Store result
        task_context.nodes[self.node_name] = {
            "response_model": deleted_events,
        }

        logger.info(
            "Deleted %d event%s from calendar",
            len(deleted_events.items),
            "" if len(deleted_events.items) == 1 else "s",
        )

        return task_context
