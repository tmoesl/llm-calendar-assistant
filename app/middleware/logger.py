"""
Middleware Module

This middleware automatically injects request-specific context into logs.
It generates correlation IDs for the API request. Passed to Celery tasks.
"""

import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.services.logger_factory import set_request_id


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to set the request ID for the API request.
    """

    async def dispatch(self, request: Request, call_next):
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())[:8]

        # Set context automatically
        set_request_id(correlation_id)

        # Store correlation_id on request for later use
        request.state.correlation_id = correlation_id

        # Process request
        response = await call_next(request)

        return response
