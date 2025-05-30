"""
Repository Module

This module implements the Repository pattern for database operations.
It provides a generic repository class that can be used with any SQLAlchemy model
to perform CRUD operations in a consistent and reusable way.
"""

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy.orm import Session

from app.database.session import Base

# Type variable for SQLAlchemy models
ModelType = TypeVar("ModelType", bound=Base)


class GenericRepository(Generic[ModelType]):
    """
    Generic repository for CRUD operations on SQLAlchemy models.

    This class implements the Repository pattern, providing a consistent interface
    for database operations across different models. It encapsulates common CRUD
    operations and can be extended for model-specific functionality.

    TRANSACTION STRATEGY:
    Uses flush() + refresh() instead of immediate commit() to provide flexible
    transaction control:

    - flush(): Sends changes to DB but doesn't commit (reversible)
    - refresh(): Gets DB-generated values (IDs, timestamps) back to the object
    - Caller controls when to commit() or rollback()
    - Supports both single operations and complex multi-operation transactions
    - Works seamlessly with FastAPI's get_db_session() dependency (auto-commit)

    Attributes:
        session: SQLAlchemy database session
        model: SQLAlchemy model class

    Examples:
        # FastAPI endpoint (auto-commit via dependency)
        @app.post("/events")
        def create_event(data: dict, db: Session = Depends(get_db_session)):
            repo = GenericRepository(session=db, model=Event)
            event = repo.create(Event(data=data))  # flush() only
            return event  # Auto-commit when dependency completes

        # Manual transaction control for complex operations
        session = SessionLocal()
        try:
            repo = GenericRepository(session=session, model=Event)
            event1 = repo.create(Event(...))  # flush() - not committed yet
            event2 = repo.create(Event(...))  # flush() - not committed yet
            session.commit()  # Commit both operations together
        except Exception:
            session.rollback()  # Rollback both if any operation fails
        finally:
            session.close()

        # Simple single operation
        repo = GenericRepository(session=session, model=Event)
        event = repo.get(id=event_id)  # Read operations don't need commit
    """

    def __init__(self, session: Session, model: type[ModelType]):
        """
        Initialize the repository with a database session and model.

        Args:
            session: SQLAlchemy database session
            model: SQLAlchemy model class
        """
        self.session = session
        self.model = model

    def create(self, obj: ModelType) -> ModelType:
        """
        Create a new record in the database.

        Uses flush() + refresh() strategy:
        - flush(): Sends INSERT to DB but doesn't commit (transaction still open)
        - refresh(): Gets DB-generated values (ID, timestamps) back to object
        - Caller must commit() to persist, or rollback() to undo

        Args:
            obj: Model instance to create

        Returns:
            ModelType: The created model instance with updated fields (including DB-generated ID)

        Raises:
            SQLAlchemyError: If database operation fails

        Example:
            # In FastAPI endpoint (auto-commit)
            event = repo.create(Event(data=data))  # flush() only, auto-commit later

            # Manual transaction control
            event = repo.create(Event(data=data))  # flush() only
            session.commit()  # Now actually persisted
        """
        self.session.add(obj)
        self.session.flush()  # Send to DB but don't commit (reversible)
        self.session.refresh(obj)  # Get DB-generated values (ID, timestamps)
        return obj

    def get(self, id: UUID | str) -> ModelType | None:
        """
        Retrieve a record by its ID.

        Args:
            id: Primary key of the record to retrieve

        Returns:
            Optional[ModelType]: The model instance if found, None otherwise
        """
        return self.session.query(self.model).filter(self.model.id == id).first()

    def get_all(self, limit: int = 100, offset: int = 0) -> list[ModelType]:
        """
        Retrieve all records with pagination.

        Args:
            limit: Maximum number of records to return (default: 100)
            offset: Number of records to skip (default: 0)

        Returns:
            List[ModelType]: List of model instances
        """
        return self.session.query(self.model).offset(offset).limit(limit).all()

    def update(self, obj: ModelType) -> ModelType:
        """
        Update an existing record in the database.

        Uses flush() + refresh() strategy for transaction control.
        The update is sent to DB but not committed until caller commits.

        Args:
            obj: Model instance with updated values

        Returns:
            ModelType: The updated model instance with refreshed DB values

        Raises:
            SQLAlchemyError: If database operation fails
        """
        self.session.merge(obj)
        self.session.flush()  # Send UPDATE to DB but don't commit
        self.session.refresh(obj)  # Get updated values from DB
        return obj

    def delete(self, id: UUID | str) -> bool:
        """
        Delete a record by its ID.

        Uses flush() strategy - deletion is sent to DB but not committed
        until caller commits the transaction.

        Args:
            id: Primary key of the record to delete

        Returns:
            bool: True if record was deleted, False if not found

        Raises:
            SQLAlchemyError: If database operation fails
        """
        obj = self.get(id)
        if obj:
            self.session.delete(obj)
            self.session.flush()  # Send DELETE to DB but don't commit
            return True
        return False

    def count(self) -> int:
        """
        Count the total number of records.

        Returns:
            int: Total number of records in the table
        """
        return self.session.query(self.model).count()

    def filter_by(self, **kwargs: Any) -> list[ModelType]:
        """
        Filter records by specified criteria.

        Args:
            **kwargs: Filter criteria as keyword arguments

        Returns:
            List[ModelType]: List of matching model instances

        Example:
            # Find events by workflow type
            events = repo.filter_by(workflow_type="calendar_request")
        """
        return self.session.query(self.model).filter_by(**kwargs).all()

    def get_latest(self, limit: int = 10) -> list[ModelType]:
        """
        Retrieve the most recent records ordered by creation time.

        Args:
            limit: Maximum number of records to return (default: 10)

        Returns:
            List[ModelType]: List of model instances ordered by created_at DESC

        Example:
            # Get the 5 most recent events
            recent_events = repo.get_latest(limit=5)
        """
        return (
            self.session.query(self.model).order_by(self.model.created_at.desc()).limit(limit).all()
        )
