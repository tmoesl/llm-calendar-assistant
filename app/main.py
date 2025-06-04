"""
Main FastAPI Application Module

This module creates and configures the FastAPI application instance.
It includes all API routers and sets up the application configuration.
"""

from fastapi import FastAPI

from app.api.router import router as api_router
from app.middleware.logger import RequestContextMiddleware
from app.services.logger_config import API
from app.services.logger_factory import logger, setup_service_logger

# Setup logging for FastAPI (pure configuration)
setup_service_logger(API)

# Create FastAPI application instance
app = FastAPI()

# Add middleware before including routers
app.add_middleware(RequestContextMiddleware)

# Include API routers
app.include_router(api_router, prefix="/api/v1")

logger.info("FastAPI application initialized")
