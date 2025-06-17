"""
Celery Worker Configuration

Internal configuration for Celery application setup.
External configuration (concurrency, log level) is handled by the shell script.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerConfig(BaseSettings):
    """Internal Celery application configuration."""

    # Redis connection settings
    redis_host: str = Field(alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")

    # Worker operational settings
    concurrency: int = Field(default=4, alias="CELERY_CONCURRENCY")
    log_level: str = Field(default="DEBUG", alias="CELERY_LOG_LEVEL")

    @property
    def redis_url(self) -> str:
        """Redis URL for Celery broker."""
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    @property
    def celery_settings(self) -> dict:
        """Celery application configuration with production standards."""
        return {
            # --- Connection ---
            "broker_url": self.redis_url,
            "result_backend": self.redis_url,
            # --- Worker Settings ---
            "worker_concurrency": self.concurrency,
            "worker_loglevel": self.log_level,
            # --- Production Standards (hardcoded) ---
            "broker_connection_retry_on_startup": True,
            "task_serializer": "json",
            "accept_content": ["json"],
            "result_serializer": "json",
            "enable_utc": True,
            "worker_max_tasks_per_child": 1000,
            "worker_pool": "prefork",
            "worker_heartbeat": 10,
            "worker_prefetch_multiplier": 1,
            "task_time_limit": 300,
            "task_soft_time_limit": 240,
            "task_send_sent_event": True,
            "task_track_started": True,
            "worker_send_task_events": True,
            "task_annotations": {"*": {"rate_limit": "10/s"}},
            "task_routes": {"app.worker.tasks.*": {"queue": "default"}},
        }

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_worker_config() -> WorkerConfig:
    """
    Get the worker configuration. Uses lru_cache to avoid repeated loading

    Returns:
        WorkerConfig: The worker configuration.
    """
    return WorkerConfig()
