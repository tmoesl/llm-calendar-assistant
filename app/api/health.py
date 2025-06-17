"""
Health Check API Module

Exposes endpoints to monitor application status and dependencies. The module uses SQLAlchemy to
check database connectivity, Redis for cache health, and Celery for worker status.
It also includes an optional Flower monitoring service check.

The module is designed to be used by load balancers to verify service availability.
It raises HTTPException if any critical component is unhealthy.
"""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.session import get_db_session

health_router = APIRouter()

# Optional dependency availability flags
try:
    import requests  # type: ignore

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from redis import Redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from celery import Celery  # type: ignore

    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False


def _get_redis_client():
    """Get Redis client for health checks."""
    if not REDIS_AVAILABLE:
        raise ImportError("Redis library not available")

    from app.worker.celery_app import celery_app

    # Extract Redis URL from Celery configuration
    redis_url = celery_app.conf.broker_url
    return Redis.from_url(redis_url, decode_responses=True)


def _get_celery_app():
    """Get Celery app for health checks."""
    if not CELERY_AVAILABLE:
        raise ImportError("Celery library not available")

    from app.worker.celery_app import celery_app

    return celery_app


def _check_database(db: Session) -> dict[str, str]:
    """Check database connectivity."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "message": "Database connection successful"}
    except Exception as e:
        return {"status": "unhealthy", "message": f"Database connection failed: {str(e)}"}


def _check_redis() -> dict[str, str]:
    """Check Redis connectivity."""
    try:
        redis_client = _get_redis_client()
        redis_client.ping()
        return {"status": "healthy", "message": "Redis connection successful"}
    except Exception as e:
        return {"status": "unhealthy", "message": f"Redis connection failed: {str(e)}"}


def _check_celery() -> dict[str, Any]:
    """Check Celery worker connectivity."""
    try:
        celery_app = _get_celery_app()
        inspect = celery_app.control.inspect()
        active_workers = inspect.ping()

        if active_workers:
            return {
                "status": "healthy",
                "message": f"Celery workers active: {len(active_workers)}",
                "workers": list(active_workers.keys()),
            }
        else:
            return {"status": "unhealthy", "message": "No active Celery workers found"}
    except Exception as e:
        return {"status": "unhealthy", "message": f"Celery worker check failed: {str(e)}"}


def _check_flower() -> dict[str, str]:
    """Check Flower monitoring service."""
    if not REQUESTS_AVAILABLE:
        return {
            "status": "unavailable",
            "message": "Requests library not available for Flower check",
        }

    try:
        response = requests.get("http://localhost:5555", timeout=5)
        if response.status_code == 200 and "Flower" in response.text:
            return {"status": "healthy", "message": "Flower monitoring service accessible"}
        else:
            return {
                "status": "unhealthy",
                "message": f"Flower returned status code: {response.status_code}",
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Flower monitoring service check failed: {str(e)}",
        }


@health_router.get("")
async def basic_health() -> dict[str, Any]:
    """
    Basic health check - always returns healthy.
    Used by load balancers to verify service availability.
    """
    return {
        "status": "healthy",
        "service": "llm-calendar-assistant-api",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@health_router.get("/ready")
async def readiness_check(
    check_flower: bool = Query(False, description="Include Flower monitoring service check"),
    db: Session = Depends(get_db_session),  # noqa: B008
) -> dict[str, Any]:
    """
    Comprehensive readiness check for all critical services.

    Raises:
        HTTPException: 503 if any critical component is unhealthy
    """
    health_status: dict[str, Any] = {
        "status": "ready",
        "service": "llm-calendar-assistant-api",
        "timestamp": datetime.now(UTC).isoformat(),
        "components": {
            "database": _check_database(db),
            "redis": _check_redis(),
            "celery": _check_celery(),
        },
    }

    # Add optional Flower check
    if check_flower:
        health_status["components"]["flower"] = _check_flower()

    # Check if any critical components are unhealthy (Flower is optional)
    critical_components = ["database", "redis", "celery"]
    all_healthy = all(
        health_status["components"][comp]["status"] == "healthy" for comp in critical_components
    )

    if not all_healthy:
        health_status["status"] = "not ready"
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=health_status)

    return health_status
