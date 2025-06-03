import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.services.log_service import set_request_id, set_service_tag


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to set the request ID and service tag for the request.
    """

    async def dispatch(self, request: Request, call_next):
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())[:8]

        # Set context automatically
        set_request_id(correlation_id)
        set_service_tag("api")

        # Store correlation_id on request for later use
        request.state.correlation_id = correlation_id

        # Process request
        response = await call_next(request)

        return response
