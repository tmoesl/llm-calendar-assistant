"""
Pipeline Orchestrator Module

Orchestrates the pipeline for processing calendar requests.
Implements workflow logic for routing and handling different event types.
"""

from app.core.pipeline import Pipeline
from app.core.schema.pipeline import NodeConfig, PipelineSchema
from app.pipeline.classify_event import ClassifyEvent
from app.pipeline.event.create.executor import CreateEventExecutor
from app.pipeline.event.create.extractor import CreateEventExtractor
from app.pipeline.event.delete.executor import DeleteEventExecutor
from app.pipeline.event.lookup.executor import LookupEventExecutor
from app.pipeline.event.lookup.extractor import LookupEventExtractor
from app.pipeline.route_event import RouteEvent
from app.pipeline.validate_event import ValidateEvent

# from app.pipeline.extractors.update import UpdateEventExtractor
# from app.pipeline.extractors.view import ViewEventExtractor


class CalendarPipeline(Pipeline):
    """Linear pipeline for processing calendar requests

    Each node updates the EventContext status and metadata, passing it to the next node.
    Router determines which handler to use, EventLookup finds existing events if needed,
    and final handler node executes the calendar operation.
    """

    pipeline_schema = PipelineSchema(
        description="Pipeline for handling calendar operations",
        start=ValidateEvent,
        nodes=[
            # Security and validation
            NodeConfig(
                node=ValidateEvent,
                connections=[ClassifyEvent],
                description="Validate input security and legitimacy",
            ),
            # Intent classification
            NodeConfig(
                node=ClassifyEvent,
                connections=[RouteEvent],
                description="Classify the calendar operation intent",
            ),
            # Event Routing
            NodeConfig(
                node=RouteEvent,
                connections=[CreateEventExtractor, LookupEventExtractor],
                description="Extract raw event details",
                is_router=True,
            ),
            # Operation-specific nodes
            NodeConfig(
                node=CreateEventExtractor,
                connections=[CreateEventExecutor],
                description="Extract create-specific details",
            ),
            NodeConfig(
                node=CreateEventExecutor,
                connections=[],  # End node
                description="Execute event creation in Google Calendar",
            ),
            NodeConfig(
                node=LookupEventExtractor,
                connections=[LookupEventExecutor],
                description="Extract generic lookup details for an event",
            ),
            NodeConfig(
                node=LookupEventExecutor,
                connections=[DeleteEventExecutor],
                description="Look up events matching search criteria",
            ),
            NodeConfig(
                node=DeleteEventExecutor,
                connections=[],  # End node
                description="Execute event deletion in Google Calendar",
            ),
            # ... similar configs for update/view
        ],
    )
