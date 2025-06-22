"""
Database Configuration

Configuration for database service including connection settings,
pool configuration, and environment-specific behavior.
"""

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DbConfig(BaseSettings):
    """Database service configuration."""

    # Database connection settings
    host: str = Field(alias="DATABASE_HOST")
    password: SecretStr = Field(alias="DATABASE_PASSWORD")
    user: str = Field(alias="DATABASE_USER")
    name: str = Field(default="postgres", alias="DATABASE_NAME")
    port: int = Field(default=6543, alias="DATABASE_PORT")

    @property
    def url(self) -> str:
        """PostgreSQL connection string."""
        return f"postgresql://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.name}"

    @property
    def engine_options(self) -> dict:
        """SQLAlchemy engine options with PostgreSQL standards."""
        return {
            # --- Production Standards (hardcoded) ---
            "pool_size": 5,
            "max_overflow": 0,
            "pool_timeout": 30,
            "pool_pre_ping": True,
            "pool_recycle": 3600,  # 1 hour
            "echo": False,
        }

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_db_config() -> DbConfig:
    """
    Get the database configuration. Uses lru_cache to avoid repeated loading

    Returns:
        DbConfig: The database configuration.
    """
    return DbConfig()
