"""
Logging Factory

Handles logger creation, context management, and runtime logging behavior.
Provides the main logging interface for the application.
"""

import logging
import sys
from contextvars import ContextVar
from pathlib import Path

from app.services.logger_config import LogConfig, get_log_config

# Context variable to store current request ID
_request_id: ContextVar[str] = ContextVar("request_id", default="--------")

# Context variable to store current service tag
_service_tag: ContextVar[str] = ContextVar("service_tag", default="main")


class TaskFormatter(logging.Formatter):
    """Custom formatter that automatically includes Service Tag and Request ID from context"""

    def format(self, record):
        service_tag = _service_tag.get()
        request_id = _request_id.get()
        record.service_tag = f"[{service_tag}]"
        record.request_id = f"[req:{request_id}]"
        return super().format(record)


def set_request_id(request_id: str):
    """Set the current request ID (auto-shortened to 8 chars)"""
    _request_id.set(str(request_id)[:8])


def set_service_tag(service: str):
    """Set the current service tag (api, celery, pipeline, etc.)"""
    _service_tag.set(service)


def setup_service_logger(service_name: str, config: LogConfig | None = None) -> None:
    """
    Set up logging configuration for the application.

    This function configures handlers, formatters, and initial service context.
    Use this ONLY at application entry points (FastAPI startup, Celery worker startup).
    This function is idempotent - safe to call multiple times.

    Args:
        service_name: Name of the service (e.g., "api", "celery")
        config: Optional log configuration. If None, uses default config.
    """
    if config is None:
        config = get_log_config()

    logger = logging.getLogger(config.name)

    # Check if logging is already configured
    if logger.handlers:
        set_service_tag(service_name)
        return

    # Set up logging configuration
    logger.setLevel(getattr(logging, config.level))

    # Create custom formatter with service tag and request ID support
    formatter = TaskFormatter(
        config.format,
        datefmt=config.date_format,
    )

    # Create and add handlers based on configuration
    if config.file_output:
        # Ensure logs directory exists
        log_path = Path(config.file_path)
        log_path.parent.mkdir(exist_ok=True)

        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if config.console_output:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    # Set propagation based on configuration
    logger.propagate = config.propagate

    # Set service tag for this service
    set_service_tag(service_name)
    logger.info(f"Logger initialized for service: {service_name}")


# ================================ BASE LOGGER ================================
# Loaded when the module is imported
# Configured when setup_service_logger() is called

config = get_log_config()
logger = logging.getLogger(config.name)
