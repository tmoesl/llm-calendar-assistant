"""
Health Check API Module

This module provides simplified health check endpoints for monitoring the application status,
database connectivity, Redis connectivity, Celery workers, and optionally Flower monitoring.
"""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.session import get_db_session

router = APIRouter()

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from redis import Redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from celery import Celery

    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False


def get_redis_client():
    """Get Redis client for health checks."""
    if not REDIS_AVAILABLE:
        raise ImportError("Redis library not available")

    try:
        from app.worker.config import get_worker_config

        worker_config = get_worker_config()
        return Redis.from_url(worker_config.redis_url, decode_responses=True)
    except Exception as e:
        raise ConnectionError(f"Failed to create Redis client: {str(e)}")


def get_celery_app():
    """Get Celery app for health checks."""
    if not CELERY_AVAILABLE:
        raise ImportError("Celery library not available")

    try:
        from app.worker.celery_app import celery_app

        return celery_app
    except Exception as e:
        raise ImportError(f"Failed to import Celery app: {str(e)}")


@router.get("/health")
async def basic_health() -> dict[str, Any]:
    """
    Basic health check endpoint - always returns healthy.
    Used by load balancers to verify the service is alive.

    Returns:
        Dict containing basic health status and timestamp
    """
    return {
        "status": "healthy",
        "service": "llm-calendar-assistant-api",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/health/ready")
async def readiness_check(
    check_flower: bool = Query(False, description="Include Flower monitoring service check"),
    db: Session = Depends(get_db_session),
) -> dict[str, Any]:
    """
    Comprehensive readiness check endpoint.
    Verifies all critical services (DB, Redis, Celery) and optionally Flower.

    Args:
        check_flower: Whether to include Flower monitoring service in health check
        db: Database session dependency

    Returns:
        Dict containing detailed health status of all components

    Raises:
        HTTPException: If any critical component is unhealthy
    """
    health_status = {
        "status": "ready",
        "service": "llm-calendar-assistant-api",
        "timestamp": datetime.now(UTC).isoformat(),
        "components": {},
    }

    all_healthy = True

    # Check database connectivity
    try:
        db.execute(text("SELECT 1"))
        health_status["components"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful",
        }
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}",
        }
        all_healthy = False

    # Check Redis connectivity
    try:
        redis_client = get_redis_client()
        redis_client.ping()
        health_status["components"]["redis"] = {
            "status": "healthy",
            "message": "Redis connection successful",
        }
    except Exception as e:
        health_status["components"]["redis"] = {
            "status": "unhealthy",
            "message": f"Redis connection failed: {str(e)}",
        }
        all_healthy = False

    # Check Celery worker connectivity (required)
    try:
        celery_app = get_celery_app()
        # Ping active workers
        inspect = celery_app.control.inspect()
        active_workers = inspect.ping()

        if active_workers:
            worker_count = len(active_workers)
            worker_names = list(active_workers.keys())
            health_status["components"]["celery"] = {
                "status": "healthy",
                "message": f"Celery workers active: {worker_count}",
                "workers": worker_names,
            }
        else:
            health_status["components"]["celery"] = {
                "status": "unhealthy",
                "message": "No active Celery workers found",
            }
            all_healthy = False
    except Exception as e:
        health_status["components"]["celery"] = {
            "status": "unhealthy",
            "message": f"Celery worker check failed: {str(e)}",
        }
        all_healthy = False

    # Check Flower monitoring service (optional)
    if check_flower:
        if not REQUESTS_AVAILABLE:
            health_status["components"]["flower"] = {
                "status": "unavailable",
                "message": "Requests library not available for Flower check",
            }
        else:
            try:
                # Check Flower web interface instead of API (API requires auth)
                flower_url = "http://localhost:5555"
                response = requests.get(flower_url, timeout=5)
                if response.status_code == 200 and "Flower" in response.text:
                    health_status["components"]["flower"] = {
                        "status": "healthy",
                        "message": "Flower monitoring service accessible",
                    }
                else:
                    health_status["components"]["flower"] = {
                        "status": "unhealthy",
                        "message": f"Flower returned status code: {response.status_code}",
                    }
                    # Flower is optional, so don't mark overall as unhealthy
            except Exception as e:
                health_status["components"]["flower"] = {
                    "status": "unhealthy",
                    "message": f"Flower monitoring service check failed: {str(e)}",
                }
                # Flower is optional, so don't mark overall as unhealthy

    # Update overall status
    if not all_healthy:
        health_status["status"] = "not ready"
        raise HTTPException(status_code=503, detail=health_status)

    return health_status
