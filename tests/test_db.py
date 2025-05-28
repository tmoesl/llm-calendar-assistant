"""
Test Database Module

This module contains test fixtures and utilities for testing the database interactions
within the application. It sets up the necessary database tables and provides a session
for executing tests against the database.
"""

import uuid
from collections.abc import Generator
from typing import Any, cast

import pytest
from sqlalchemy.orm import Session

from app.database.database_utils import DatabaseUtils  # To potentially check connection string
from app.database.event import Event  # Assuming your Event model is here
from app.database.repository import GenericRepository
from app.database.session import SessionLocal


# Fixture to create tables once per session if they don't exist
# For a real test suite, you might want a dedicated test database
# and more sophisticated setup/teardown (e.g., using testcontainers)
@pytest.fixture(scope="session", autouse=True)
def create_test_tables() -> Generator[None, Any, None]:
    """
    Fixture to ensure the database is accessible.
    It is assumed that migrations (e.g., alembic upgrade head) have been run
    prior to executing the test suite to set up the database schema.
    """
    # Check if the connection string can be retrieved, as a basic sanity check
    assert DatabaseUtils.get_connection_string() is not None
    # No explicit table creation or dropping is done by this fixture.
    # The database schema is expected to be managed by Alembic migrations.
    yield
    # If you had Base.metadata.drop_all(bind=engine) here, it would also be removed
    # or remain commented out to align with migration-managed schema.


@pytest.fixture
def db_session() -> Generator[Session, Any, None]:
    """Provides a database session for a test that is always rolled back."""
    session = SessionLocal()
    session.begin_nested()  # Start a nested transaction
    try:
        yield session
    finally:
        session.rollback()  # Always rollback to ensure test isolation
        session.close()


@pytest.fixture
def event_repository(db_session: Session) -> GenericRepository[Event]:
    """Provides a GenericRepository for the Event model."""
    return GenericRepository[Event](session=db_session, model=Event)


def test_database_connection(db_session: Session):
    """Test that a database session can be established and is active."""
    assert db_session.is_active


def test_create_event(event_repository: GenericRepository[Event]):
    """Test creating a new event."""
    event_data = {
        "workflow_type": "test_workflow",
        "data": {"key": "value", "details": "some test data"},
    }
    new_event_instance = Event(**event_data)

    created_event = event_repository.create(new_event_instance)
    # The create method in GenericRepository already does flush and refresh.
    # db_session.flush() # Not strictly necessary here if repo handles it

    assert created_event.id is not None
    assert isinstance(created_event.id, uuid.UUID)
    assert created_event.workflow_type == event_data["workflow_type"]
    assert created_event.data == event_data["data"]
    assert created_event.created_at is not None
    assert created_event.updated_at is not None

    # Clean up the created event to keep tests isolated if not using transaction rollback for cleanup
    # For this setup, the session fixture handles rollback on failure, commit on success.
    # If you want to be absolutely sure it's gone for other tests, you can delete here.
    # db_session.delete(created_event)
    # db_session.commit()


def test_get_event(event_repository: GenericRepository[Event]):
    """Test retrieving an event by its ID."""
    event_data = {
        "workflow_type": "get_test_workflow",
        "data": {"retrieval_key": "retrieval_value"},
    }
    new_event_instance = Event(**event_data)
    created_event = event_repository.create(new_event_instance)
    # db_session.flush() # Not strictly necessary here

    # Ensure created_event.id is the actual UUID value
    event_id_value = cast(uuid.UUID, created_event.id)
    fetched_event = event_repository.get(id=event_id_value)

    assert fetched_event is not None
    assert fetched_event.id == event_id_value
    assert fetched_event.workflow_type == event_data["workflow_type"]


def test_update_event(event_repository: GenericRepository[Event]):
    """Test updating an existing event."""
    event_data = {
        "workflow_type": "update_test_workflow",
        "data": {"original_key": "original_value"},
    }
    new_event_instance = Event(**event_data)
    created_event = event_repository.create(new_event_instance)
    # db_session.flush()

    updated_data_payload = {"original_key": "updated_value", "new_key": "new_value"}

    # To update, you typically modify the fetched object's attributes
    # The GenericRepository.update() method uses session.merge()
    # which is suitable if 'created_event' might be detached or you're passing a new instance with the same ID.
    # If 'created_event' is still attached to the session, direct modification is also common.

    # Let's simulate fetching it (or using the already attached 'created_event') and modifying
    event_id_value = cast(uuid.UUID, created_event.id)
    event_to_update = event_repository.get(id=event_id_value)
    assert event_to_update is not None

    event_to_update.data = updated_data_payload
    event_to_update.workflow_type = "updated_workflow_type"

    updated_event = event_repository.update(event_to_update)
    # db_session.flush()

    assert updated_event is not None
    assert updated_event.id == event_id_value
    assert updated_event.data == updated_data_payload
    assert updated_event.workflow_type == "updated_workflow_type"
    # Timestamps should ideally be different or handled by DB on update
    # assert updated_event.updated_at > created_event.updated_at


def test_delete_event(event_repository: GenericRepository[Event]):
    """Test deleting an event."""
    event_data = {"workflow_type": "delete_test_workflow", "data": {"delete_key": "delete_value"}}
    new_event_instance = Event(**event_data)
    created_event = event_repository.create(new_event_instance)
    # db_session.flush()

    event_id_value = cast(uuid.UUID, created_event.id)
    # Re-fetch to ensure we are checking existence from DB before delete
    assert event_repository.get(id=event_id_value) is not None

    delete_successful = event_repository.delete(id=event_id_value)
    # db_session.flush() # Not strictly necessary if repo handles it

    assert delete_successful is True
    assert event_repository.get(id=event_id_value) is None


def test_get_all_events_and_count(event_repository: GenericRepository[Event]):
    """Test retrieving all events and counting them."""
    # Clear out existing events for a cleaner count test, or ensure this runs in a transaction
    # For simplicity, we'll assume a relatively clean slate or count existing ones.

    initial_count = event_repository.count()

    event_data1 = {"workflow_type": "all_test_1", "data": {"k1": "v1"}}
    event_data2 = {"workflow_type": "all_test_2", "data": {"k2": "v2"}}

    event_repository.create(Event(**event_data1))
    event_repository.create(Event(**event_data2))
    # db_session.flush()

    assert event_repository.count() == initial_count + 2

    all_events = event_repository.get_all(limit=10)
    # This assertion might be flaky if tests run in parallel or if the db is not cleaned per test.
    # For this example, we assume a relatively controlled environment or accept this could be >=.
    assert len(all_events) >= initial_count + 2

    found_event1_data = [e.data for e in all_events if e.workflow_type == "all_test_1"]
    found_event2_data = [e.data for e in all_events if e.workflow_type == "all_test_2"]
    assert event_data1["data"] in found_event1_data
    assert event_data2["data"] in found_event2_data


def test_filter_by_events(event_repository: GenericRepository[Event]):
    """Test filtering events by criteria."""

    unique_workflow_type = (
        f"filter_test_{uuid.uuid4()}"  # Ensure unique workflow type for this test
    )

    event_data1 = {"workflow_type": unique_workflow_type, "data": {"filter_key": "val1"}}
    event_data2 = {"workflow_type": unique_workflow_type, "data": {"filter_key": "val2"}}
    event_data3 = {"workflow_type": "other_workflow_filter", "data": {"filter_key": "val3"}}

    event_repository.create(Event(**event_data1))
    event_repository.create(Event(**event_data2))
    event_repository.create(Event(**event_data3))
    # db_session.flush()

    filtered_events = event_repository.filter_by(workflow_type=unique_workflow_type)
    assert len(filtered_events) == 2
    for event_item in filtered_events:
        assert event_item.workflow_type == unique_workflow_type

    other_events = event_repository.filter_by(workflow_type="other_workflow_filter")
    assert len(other_events) == 1
    assert other_events[0].data == event_data3["data"]
