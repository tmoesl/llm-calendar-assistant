from contextlib import contextmanager

from app.api.schema import EventSchema
from app.database.event import Event
from app.database.repository import GenericRepository
from app.database.session import get_db_session
from app.pipeline.pipeline import CalendarPipeline
from app.services.log_service import logger
from app.worker.celery_app import celery_app

"""
Pipeline Task Processing Module

This module handles asynchronous processing of pipeline events using Celery.
It manages the lifecycle of event processing from database retrieval through
pipeline execution and result storage.
"""


@celery_app.task(name="process_incoming_event")
def process_incoming_event(event_id: str):
    """Processes an incoming event through its designated pipeline.

    This Celery task handles the asynchronous processing of events by:
    1. Retrieving the event from the database
    2. Determining the appropriate pipeline
    3. Executing the pipeline
    4. Storing the results

    Args:
        event_id: Unique identifier of the event to process
    """
    with contextmanager(get_db_session)() as session:
        # Initialize repository for database operations
        repository = GenericRepository(session=session, model=Event)

        # Retrieve event from database
        db_event = repository.get(id=event_id)
        if db_event is None:
            raise ValueError(f"Event with id {event_id} not found")

        # Convert JSON data to EventSchema
        event_data = EventSchema.model_validate(db_event.data)
        logger.info("Starting event processing")

        # Execute pipeline and store results
        pipeline = CalendarPipeline()
        task_context = pipeline.run(event_data).model_dump(mode="json")
        logger.info("Completed event processing")

        # Update event with processing results
        db_event.task_context = task_context  # type: ignore
        repository.update(obj=db_event)
        logger.info("Stored processing results")
