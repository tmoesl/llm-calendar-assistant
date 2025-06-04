"""
Main FastAPI Application Module

This module creates and configures the FastAPI application instance.
It includes all API routers and sets up the application configuration.
"""

from fastapi import FastAPI

from app.api.router import router as api_router
from app.services.log_service import logger

# Create FastAPI application instance
app = FastAPI()

# Include API routers
app.include_router(api_router, prefix="/api/v1")

logger.info("FastAPI application initialized")
