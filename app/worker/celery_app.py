import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()


def get_redis_url():
    """
    Get the Redis URL for Celery configuration.

    Returns:
        str: The Redis URL.
    """
    if os.getenv("DEV_MODE") == "true":
        # Local development: use localhost
        redis_host = os.getenv("REDIS_HOST", "localhost")
    else:
        # Docker Compose or production: use service name
        redis_host = f"{os.getenv('PROJECT_NAME')}_redis"

    redis_port = os.getenv("REDIS_PORT", "6379")
    redis_db = os.getenv("REDIS_DB", "0")

    return f"redis://{redis_host}:{redis_port}/{redis_db}"


def get_celery_config():
    """
    Get the Celery configuration.

    Returns:
        dict: The Celery configuration.
    """
    redis_url = get_redis_url()
    return {
        "broker_url": redis_url,
        "result_backend": redis_url,
        "task_serializer": "json",
        "accept_content": ["json"],
        "result_serializer": "json",
        "enable_utc": True,
        "broker_connection_retry_on_startup": True,
    }


celery_app = Celery("tasks")
celery_app.config_from_object(get_celery_config())

# Automatically discover and register tasks
celery_app.autodiscover_tasks(["app.worker"], force=True)
