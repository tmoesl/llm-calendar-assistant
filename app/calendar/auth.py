"""
Google Calendar authentication module

Handles OAuth2 authentication and token management.
"""

import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build

from app.services.logger_factory import logger

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GoogleAuthClient:
    """Handles Google OAuth 2.0 flow and service object creation."""

    def __init__(
        self, token_path: str = "token.json", creds_path: str = "credentials.json"
    ) -> None:
        self.token_path = token_path
        self.creds_path = creds_path
        self._credentials: Credentials | None = None
        self._service: Resource | None = None

    def _save_credentials(self, creds: Credentials) -> None:
        """Save the credentials to a file."""
        try:
            with open(self.token_path, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
        except Exception as e:
            logger.error("Failed to save credentials: %s", e)

    def _load_or_refresh_credentials(self) -> Credentials | None:
        """Load credentials from file, refresh if needed, or trigger OAuth flow."""
        creds = None
        # Try to load existing token
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

            # If loaded credentials need refresh, try refreshing
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    self._save_credentials(creds)
                except Exception as e:
                    logger.error("Failed to refresh credentials: %s", e)
                    creds = None

        # No valid credentials available, run OAuth flow
        if not creds or not creds.valid:
            creds = self._run_oauth_flow()

        return creds

    def _run_oauth_flow(self) -> Credentials | None:
        """Run the OAuth flow to obtain new credentials."""
        try:
            flow = InstalledAppFlow.from_client_secrets_file(self.creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
            self._save_credentials(creds)
            return creds
        except Exception as e:
            logger.error("OAuth flow failed: %s", e)
            return None

    def authenticate(self, api_name: str = "calendar", api_version: str = "v3") -> Resource:
        """Authenticate and return a Google API service object."""
        # Return cached service if valid
        if self._service and self._credentials and self._credentials.valid:
            return self._service

        # Get fresh credentials
        self._credentials = self._load_or_refresh_credentials()
        if not self._credentials:
            raise ConnectionError("Failed to obtain valid Google credentials.")

        try:
            self._service = build(
                api_name, api_version, credentials=self._credentials, cache_discovery=False
            )
            return self._service
        except Exception as e:
            raise ConnectionError(f"Failed to build {api_name} service: {e}")
