"""
Lookup event node for the pipeline.
Handles the retrieval of calendar events.
"""

from app.calendar.auth import GoogleAuthClient
from app.calendar.schema import lookup_event_model_to_request
from app.calendar.service import GoogleCalendarService
from app.core.node import Node
from app.core.schema.llm import LlmEventLookup
from app.core.schema.task import TaskContext
from app.services.log_service import logger


class LookupEventExecutor(Node):
    """Node to execute event lookup based on extracted details."""

    def __init__(self):
        """Initialize with Google Calendar client."""
        self.client = GoogleAuthClient()
        logger.info("Initialized %s", self.node_name)

    def process(self, task_context: TaskContext) -> TaskContext:
        """Look up events using search criteria."""
        try:
            # Get search criteria from extractor
            extractor_result = task_context.nodes.get("DeleteEventExtractor", {})
            if extractor_result.get("status") != "success":
                raise ValueError("Missing or failed lookup criteria")

            # Get validated search parameters
            search_params: LlmEventLookup = extractor_result["response_model"]

            # Initialize calendar service
            service = self.client.authenticate()
            calendar_service = GoogleCalendarService(service)

            # Find matching events
            if search_params.event_id:
                # Direct event ID lookup using events.get
                event = calendar_service.get_event(
                    calendar_id="primary", event_id=search_params.event_id
                )
                found_events = [event] if event else []
            else:
                # Search by criteria using events.list
                if not search_params.time_window:
                    raise ValueError("Time window is required for event search")

                lookup_request = lookup_event_model_to_request(model=search_params)
                found_events = calendar_service.list_events(
                    calendar_id="primary",
                    **lookup_request.model_dump(exclude_none=True),
                )

            # Validate results
            if not found_events:
                ref = (
                    search_params.time_window.original_reference
                    if search_params.time_window
                    else search_params.event_id
                )
                raise ValueError(f"No events found matching criteria: {ref}")

            if len(found_events) > 1:
                event_summaries = [
                    f"'{event.get('summary', 'Unknown')}' at {event['start'].get('dateTime', event['start'].get('date'))}"
                    for event in found_events
                ]
                logger.debug(
                    "Found %d matching events:\n%s",
                    len(found_events),
                    "\n".join(f"- {summary}" for summary in event_summaries),
                )
                raise ValueError(
                    f"Found {len(found_events)} matching events. Please provide more specific criteria."
                )

            # Store result with raw event data
            task_context.nodes[self.node_name] = {
                "status": "success",
                "found_events": found_events,
            }

            logger.info("Found matching event: '%s'", found_events[0].get("summary", "Unknown"))

        except Exception as e:
            logger.error("Failed to look up events: %s", str(e))
            task_context.nodes[self.node_name] = {"status": "error", "error": str(e)}

        return task_context
