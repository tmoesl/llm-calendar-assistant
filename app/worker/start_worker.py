"""
Celery Worker Startup Script

This script sets up logging for Celery workers and imports the celery app.
Use this as the entry point for celery workers.
"""

from app.logging.config import WORKER
from app.logging.factory import logger, setup_service_logger
from app.worker.celery_app import celery_app

# Setup logging for Celery worker (pure configuration)
setup_service_logger(WORKER)

# Celery celery application instance
app = celery_app

logger.info("Celery worker initialized")
