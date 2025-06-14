"""
Calendar Authentication Router

Handles calendar authentication operations such as checking authentication status,
revoking stored credentials, and initiating re-authentication when required.
Ensures secure and reliable access to calendar features by managing OAuth tokens.
"""

from fastapi import APIRouter, HTTPException, status

from app.calendar.auth import AuthenticationError, GoogleAuthClient
from app.logging.factory import logger

calendar_router = APIRouter()


@calendar_router.get("/status")
async def get_auth_status():
    """
    Check current authentication status.

    Returns:
        dict: Authentication status information

    Raises:
        HTTPException: 401 for expired credentials, 500 for system errors
    """
    try:
        client = GoogleAuthClient()
        creds = client._load_existing_credentials()

        if creds and creds.valid:
            return {
                "status": "authenticated",
                "message": "Successfully authenticated with Google Calendar",
            }
        elif creds and creds.expired:
            # Credentials exist but are expired
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credentials have expired. Please re-authenticate.",
            )
        else:
            return {
                "status": "unauthenticated",
                "message": "No valid credentials found. Please authenticate.",
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to check authentication status: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check authentication status",
        ) from e


@calendar_router.post("/revoke")
async def revoke_auth():
    """
    Revoke current calendar authentication.

    Returns:
        dict: Revocation status

    Raises:
        HTTPException: 500 for authentication or system errors
    """
    try:
        client = GoogleAuthClient()
        client.revoke_credentials()
        return {"status": "revoked", "message": "Successfully revoked calendar authentication"}

    except AuthenticationError as e:
        logger.error("Failed to revoke authentication: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke authentication: {e}",
        ) from e
    except Exception as e:
        logger.error("Unexpected error during credential revocation: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke authentication",
        ) from e
