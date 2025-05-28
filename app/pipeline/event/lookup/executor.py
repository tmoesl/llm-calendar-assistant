"""
Lookup event node for the pipeline.
Handles the retrieval of calendar events.
"""

from app.calendar.auth import GoogleAuthClient
from app.calendar.schema import (
    GoogleEventResponse,
    GoogleLookupEventResponse,
    lookup_event_model_to_request,
)
from app.calendar.service import GoogleCalendarService
from app.core.node import Node
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
            extractor_result = task_context.nodes.get("LookupEventExtractor", {})
            if extractor_result.get("status") != "success":
                raise ValueError("Missing or failed lookup criteria")

            # Get validated search parameters
            search_params = extractor_result["response_model"]

            # Initialize calendar service
            service = self.client.authenticate()
            calendar_service = GoogleCalendarService(service)

            # Find matching events
            if search_params.event_id:
                # Direct event ID lookup using events.get
                event_raw = calendar_service.get_event(
                    calendar_id="primary", event_id=search_params.event_id
                )
                events_raw = [event_raw] if event_raw else []
            else:
                # Search by criteria using events.list
                if not search_params.time_window:
                    raise ValueError("Time window is required for event search")

                lookup_request = lookup_event_model_to_request(model=search_params)
                events_raw = calendar_service.list_events(
                    calendar_id="primary",
                    **lookup_request.model_dump(exclude_none=True),
                )

            # Validate each event with schema
            validated_events = [GoogleEventResponse(**event) for event in events_raw if event]

            # Create lookup response
            found_events = GoogleLookupEventResponse(items=validated_events)

            # Validate results
            if not found_events.items:
                ref = (
                    search_params.time_window.original_reference
                    if search_params.time_window
                    else search_params.event_id
                )
                raise ValueError(f"No events found matching criteria: {ref}")

            # Store results
            task_context.nodes[self.node_name] = {
                "status": "success",
                "response_model": found_events,
            }

            logger.info(
                "Found %d events matching criteria",
                len(found_events.items),
            )

            # Log detailed event information
            for event in found_events.items:
                logger.debug(
                    "Event: id=%s, summary='%s', start=%s, end=%s, link=%s",
                    event.id,
                    event.summary,
                    event.start.dateTime or event.start.date,
                    event.end.dateTime or event.end.date,
                    event.htmlLink,
                )

        except Exception as e:
            logger.error("Failed to lookup events: %s", str(e))
            task_context.nodes[self.node_name] = {"status": "error", "error": str(e)}

        return task_context
