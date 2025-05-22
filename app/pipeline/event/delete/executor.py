"""
Delete Event Executor Module

Execution node for event deletion in the pipeline.
Handles the deletion of calendar events using the Google Calendar API.
"""

from app.calendar.auth import GoogleAuthClient
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
        """Delete event using lookup results."""
        try:
            # Get lookup results
            lookup_result = task_context.nodes.get("LookupEventExecutor", {})
            if lookup_result.get("status") != "success":
                raise ValueError("Missing or failed event lookup")

            # Get the event to delete (lookup ensures exactly one match)
            event = lookup_result["found_events"][0]

            # Initialize calendar service
            service = self.client.authenticate()
            calendar_service = GoogleCalendarService(service)

            # Delete the event
            calendar_service.delete_event(
                calendar_id="primary",
                event_id=event["id"],
                sendUpdates="none",  # Default to no notifications
            )

            # Store result
            task_context.nodes[self.node_name] = {
                "status": "success",
                "deleted_event": event,
            }

            logger.info(
                "Deleted event: '%s' (id: %s)",
                event.get("summary", "Unknown"),
                event["id"],
            )

        except Exception as e:
            logger.error("Failed to delete event: %s", str(e))
            task_context.nodes[self.node_name] = {"status": "error", "error": str(e)}

        return task_context
