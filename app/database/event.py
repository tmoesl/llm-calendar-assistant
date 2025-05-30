"""
Event Database Model Module

This module defines the SQLAlchemy model for storing events in the database.
It provides storage for both incoming calendar requests and their processing results.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID

from app.database.session import Base


class Event(Base):
    """
    SQLAlchemy model for storing calendar events and their processing results.

    This model serves as the primary storage for both incoming calendar requests and
    their processing results. It uses JSON columns for flexible schema storage of
    both raw data and processing context.

    Attributes:
        id: Unique identifier for the event (UUID)
        workflow_type: Type of workflow associated with the event
        data: Raw event data as received from the API endpoint
        task_context: Processing results and metadata from the workflow
        created_at: Timestamp when the event was created
        updated_at: Timestamp when the event was last updated
    """

    __tablename__ = "events"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique identifier for the event",
    )

    workflow_type = Column(
        String(100),
        nullable=False,
        doc="Type of workflow associated with the event (e.g., 'calendar_request')",
    )

    data = Column(JSON, nullable=False, doc="Raw event data as received from the API endpoint")

    task_context = Column(
        JSON, nullable=True, doc="Processing results and metadata from the workflow"
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
        doc="Timestamp when the event was created",
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
        doc="Timestamp when the event was last updated",
    )

    def __repr__(self) -> str:
        """String representation of the Event model."""
        return f"<Event(id={self.id}, workflow_type='{self.workflow_type}', created_at={self.created_at})>"
