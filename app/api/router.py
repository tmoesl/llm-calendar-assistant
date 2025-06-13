from fastapi import APIRouter

from app.api import endpoint, health

"""
API Router Module

This module sets up the API router and includes all defined endpoints.
It uses FastAPI's APIRouter to group related endpoints and provide a prefix.
"""

router = APIRouter()

router.include_router(health.router, tags=["health"])
router.include_router(endpoint.router, prefix="/events", tags=["events"])
