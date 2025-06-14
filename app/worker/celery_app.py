"""
Celery Application Module

This module sets up the Celery application instance using the worker configuration.
"""

from celery import Celery

from app.worker.config import get_worker_config

# Load worker configuration
config = get_worker_config()

# Create Celery application instance
celery_app = Celery("tasks")
celery_app.config_from_object(config.celery_settings)

# Automatically discover and register tasks
celery_app.autodiscover_tasks(["app.worker"], force=True)
