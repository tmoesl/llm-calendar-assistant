"""
Delete Event Executor Module

Execution node for event deletion in the pipeline.
Handles the deletion of calendar events using the Google Calendar API.
"""

from app.calendar.auth import GoogleAuthClient
from app.calendar.schema import GoogleLookupEventResponse
from app.calendar.service import GoogleCalendarService
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
        try:
            # Get lookup results
            lookup_result = task_context.nodes.get("LookupEventExecutor", {})
            if lookup_result.get("status") != "success":
                raise ValueError("Missing or failed event lookup")

            # Get validated events to delete
            found_events = lookup_result["response_model"]
            if not isinstance(found_events, GoogleLookupEventResponse):
                raise ValueError("Invalid lookup response format")

            # Initialize calendar service
            service = self.client.authenticate()
            calendar_service = GoogleCalendarService(service)

            # Delete all found events
            deleted_events = GoogleLookupEventResponse(items=[])
            for event in found_events.items:
                # Delete the event
                calendar_service.delete_event(
                    calendar_id="primary",
                    event_id=event.id,
                    sendUpdates="none",  # Default to no notifications
                )
                deleted_events.items.append(event)

            # Store result
            task_context.nodes[self.node_name] = {
                "status": "success",
                "response_model": deleted_events,
            }

            logger.info(
                "Deleted %d events matching criteria",
                len(deleted_events.items),
            )

            # Log detailed event information
            for event in deleted_events.items:
                logger.debug(
                    "Deleted event: id=%s, summary='%s', start=%s, end=%s, link=%s",
                    event.id,
                    event.summary,
                    event.start.dateTime or event.start.date,
                    event.end.dateTime or event.end.date,
                    event.htmlLink,
                )

        except Exception as e:
            logger.error("Failed to delete events: %s", str(e))
            task_context.nodes[self.node_name] = {"status": "error", "error": str(e)}

        return task_context
