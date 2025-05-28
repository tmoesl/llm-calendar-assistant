"""
Database Utility Module

This module provides utility functions for database operations.
It includes methods for retrieving connection strings and managing database sessions.
"""

import os

from dotenv import load_dotenv

load_dotenv()


class DatabaseUtils:
    """Utility class for database operations and configuration."""

    @staticmethod
    def get_connection_string() -> str:
        """
        Get the PostgreSQL connection string from environment variables.

        Returns:
            str: The PostgreSQL connection string for SQLAlchemy

        Environment Variables:
            DATABASE_HOST: Database host (default: localhost)
            DATABASE_PORT: Database port (default: 5432)
            DATABASE_NAME: Database name (default: calendar_assistant)
            DATABASE_USER: Database user (default: postgres)
            DATABASE_PASSWORD: Database password (default: postgres)
        """
        db_host = os.getenv("DATABASE_HOST", "localhost")
        db_port = os.getenv("DATABASE_PORT", "5432")
        db_name = os.getenv("DATABASE_NAME", "calendar_assistant")
        db_user = os.getenv("DATABASE_USER", "postgres")
        db_password = os.getenv("DATABASE_PASSWORD", "postgres")

        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
