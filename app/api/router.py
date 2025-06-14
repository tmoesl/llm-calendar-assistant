"""
API Router Module

Configures the main API router using FastAPI's APIRouter.
Defines route prefixes for each module, assigns documentation tags,
and organizes endpoints for a structured API.
"""

from fastapi import APIRouter, status

from app.api.calendar import calendar_router
from app.api.event import event_router
from app.api.health import health_router

# Main API router
router = APIRouter()

# Health check endpoints
router.include_router(
    health_router,
    prefix="/health",
    tags=["health"],
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Service not ready"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
    },
)

# Event management endpoints
router.include_router(
    event_router,
    prefix="/events",
    tags=["events"],
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
    },
)

# Calendar authentication endpoints
router.include_router(
    calendar_router,
    prefix="/calendar/auth",
    tags=["calendar", "auth"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
    },
)
