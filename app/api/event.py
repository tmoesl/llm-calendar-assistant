"""
Event Submission Endpoint Module

This module defines the primary FastAPI endpoint for event ingestion.
It implements the initial handling of incoming events by:
1. Validating the incoming event data
2. Persisting the event to the database
3. Queuing an asynchronous processing task
4. Returning an acceptance response

The endpoint follows the "accept-and-delegate" pattern where:
- Events are immediately accepted if valid
- Processing is handled asynchronously via Celery
- A 202 Accepted response indicates successful queueing

This pattern ensures high availability and responsiveness of the API
while allowing for potentially long-running processing operations.
"""

import json
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.api.schema import EventSchema
from app.database.event import Event
from app.database.repository import GenericRepository
from app.database.session import get_db_session
from app.logging.factory import logger
from app.worker.celery_app import celery_app

event_router = APIRouter()


@event_router.post("/", dependencies=[])
def handle_event(
    data: EventSchema,
    request: Request,
    session: Session = Depends(get_db_session),  # noqa: B008
) -> Response:
    """Handles incoming event submissions.

    This endpoint receives events, stores them in the database,
    and queues them for asynchronous processing. It implements
    a non-blocking pattern to ensure API responsiveness.

    Args:
        data: The event data, validated against EventSchema
        request: The FastAPI request object containing correlation_id
        session: Database session injected by FastAPI dependency

    Returns:
        Response: 202 Accepted response with task ID

    Raises:
        HTTPException: 422 for validation errors, 500 for processing failures

    Note:
        The endpoint returns immediately after queueing the task.
        Use the task ID in the response to check processing status.
    """
    logger.info("Event received")

    try:
        # Store event in database
        repository = GenericRepository(session=session, model=Event)
        raw_event = data.model_dump(mode="json")
        event = Event(data=raw_event, workflow_type="calendar_pipeline")
        repository.create(obj=event)
        logger.info("Event stored in database")

        # Queue processing task with correlation_id
        task_id = celery_app.send_task(
            "process_incoming_event",
            args=[str(event.id)],  # Converts UUID to string
            kwargs={"correlation_id": request.state.correlation_id},
        )
        logger.info("Queued event processing: %s", task_id)

        return Response(
            content=json.dumps(
                {
                    "message": "Event accepted for processing",
                    "task_id": str(task_id),
                    "event_id": str(event.id),
                }
            ),
            status_code=HTTPStatus.ACCEPTED,
        )

    except Exception as e:
        logger.error("Failed to process event: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process event",
        ) from e
