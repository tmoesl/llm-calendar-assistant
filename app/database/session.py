"""
Session Module

This module provides database session management for SQLAlchemy operations.
It includes the declarative base, engine configuration, and session factory.
"""

import logging
from collections.abc import Generator

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.database.database_utils import DatabaseUtils

# Create the SQLAlchemy engine
engine = create_engine(
    DatabaseUtils.get_connection_string(),
    echo=False,  # Set to True for SQL query logging in development
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,  # Recycle connections every hour
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base for models
Base = declarative_base()


def get_db_session() -> Generator[Session, None, None]:
    """
    Database Session Dependency for FastAPI.

    This function provides a database session for each request.
    It ensures that the session is properly committed after successful operations
    and rolled back in case of exceptions.

    Yields:
        Session: SQLAlchemy database session

    Example:
        @app.get("/events")
        def get_events(db: Session = Depends(get_db_session)):
            return db.query(Event).all()
    """
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as ex:
        session.rollback()
        logging.error("Database session error: %s", str(ex))
        raise HTTPException(
            status_code=500,
            detail="Internal server error related to database operation",
        ) from ex
    except Exception as ex:
        session.rollback()
        logging.error("Unexpected session error: %s", str(ex))
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from None
    finally:
        session.close()


def create_tables():
    """
    Create all database tables.

    This function creates all tables defined by SQLAlchemy models
    that inherit from the Base class.
    """
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Drop all database tables.

    This function drops all tables defined by SQLAlchemy models.
    Use with caution - this will delete all data!
    """
    Base.metadata.drop_all(bind=engine)
