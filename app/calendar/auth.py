"""
Google Calendar authentication module

Handles OAuth2 authentication and token management with proper error handling,
dependency injection, and separation of concerns.
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build

from app.calendar.config import CalendarConfig, get_calendar_config
from app.logging.factory import logger


class AuthenticationError(Exception):
    """Custom exception for authentication-related errors."""

    pass


class GoogleAuthClient:
    """
    Handles Google OAuth 2.0 flow and service object creation.

    This class manages the complete OAuth2 lifecycle including:
    - Loading existing credentials
    - Refreshing expired tokens
    - Running OAuth flow for new credentials
    - Building authenticated service objects
    """

    def __init__(self, config: CalendarConfig | None = None) -> None:
        """
        Initialize the Google Auth client.

        Args:
            config: Calendar configuration. Defaults to shared singleton instance.
        """
        self._config = config or get_calendar_config()
        self._scopes = self._config.scopes
        self._token_path = self._config.token_path
        self._creds_path = self._config.credentials_path
        self._credentials: Credentials | None = None
        self._service: Resource | None = None

    def _save_credentials(self, creds: Credentials) -> None:
        """
        Save credentials to token file.

        Args:
            creds: Credentials to save

        Raises:
            AuthenticationError: If credentials cannot be saved
        """
        try:
            # Ensure parent directory exists
            self._token_path.parent.mkdir(parents=True, exist_ok=True)

            # Write credentials atomically
            temp_path = self._token_path.with_suffix(".tmp")
            temp_path.write_text(creds.to_json(), encoding="utf-8")
            temp_path.replace(self._token_path)

            logger.debug("Credentials saved to %s", self._token_path)

        except Exception as e:
            logger.error("Failed to save credentials to %s: %s", self._token_path, e)
            raise AuthenticationError(f"Failed to save credentials: {e}") from e

    def _load_existing_credentials(self) -> Credentials | None:
        """
        Load existing credentials from token file.

        Returns:
            Loaded credentials or None if not found/invalid
        """
        if not self._token_path.exists():
            logger.debug("Token file not found: %s", self._token_path)
            return None

        try:
            creds = Credentials.from_authorized_user_file(self._token_path, self._scopes)
            logger.debug("Loaded credentials from %s", self._token_path)
            return creds

        except Exception as e:
            logger.warning("Failed to load credentials from %s: %s", self._token_path, e)
            return None

    def _refresh_credentials(self, creds: Credentials) -> Credentials | None:
        """
        Attempt to refresh expired credentials.

        Args:
            creds: Expired credentials to refresh

        Returns:
            Refreshed credentials or None if refresh failed
        """
        if not creds.refresh_token:
            logger.warning("No refresh token available")
            return None

        try:
            logger.debug("Refreshing expired credentials")
            creds.refresh(Request())
            self._save_credentials(creds)
            return creds
        except Exception as e:
            logger.warning("Failed to refresh credentials: %s", e)
            return None

    def _run_oauth_flow(self) -> Credentials:
        """
        Run the OAuth flow to obtain new credentials.

        Returns:
            New credentials from OAuth flow

        Raises:
            AuthenticationError: If OAuth flow fails
        """
        if not self._creds_path.exists():
            raise AuthenticationError(
                f"Credentials file not found: {self._creds_path}. "
                "Please download it from Google Cloud Console."
            )

        try:
            flow = InstalledAppFlow.from_client_secrets_file(self._creds_path, self._scopes)
            creds = flow.run_local_server(port=0)
            self._save_credentials(creds)
            return creds

        except Exception as e:
            logger.error("OAuth flow failed: %s", e)
            raise AuthenticationError(f"OAuth flow failed: {e}") from e

    def authenticate(self, api_name: str = "calendar", api_version: str = "v3") -> Resource:
        """
        Authenticate and return a Google API service object.

        Args:
            api_name: Google API service name
            api_version: API version

        Returns:
            Authenticated Google API service object

        Raises:
            AuthenticationError: If authentication fails
        """
        # Return cached service if still valid
        if self._service and self._credentials and self._credentials.valid:
            return self._service

        # Get fresh credentials
        try:
            self._credentials = self._load_existing_credentials()

            # If credentials exist but are expired, try to refresh
            if self._credentials and self._credentials.expired:
                self._credentials = self._refresh_credentials(self._credentials)

            # If no valid credentials, run OAuth flow
            if not self._credentials or not self._credentials.valid:
                logger.info("Starting OAuth flow for new credentials")
                self._credentials = self._run_oauth_flow()

        except Exception as e:
            raise AuthenticationError(f"Failed to obtain valid credentials: {e}") from e

        # Build service object
        try:
            self._service = build(
                api_name, api_version, credentials=self._credentials, cache_discovery=False
            )
            if not self._service:
                raise AuthenticationError(f"Failed to build {api_name} service: service is None")
            logger.debug("Built %s service (v%s)", api_name, api_version)
            return self._service

        except Exception as e:
            logger.error("Failed to build %s service: %s", api_name, e)
            raise AuthenticationError(f"Failed to build {api_name} service: {e}") from e

    def revoke_credentials(self) -> None:
        """
        Revoke current credentials and remove token file.

        Raises:
            AuthenticationError: If revocation fails
        """
        if self._credentials:
            try:
                self._credentials.revoke(Request())
                logger.debug("Credentials revoked")
            except Exception as e:
                logger.warning("Failed to revoke credentials: %s", e)

        # Clear cached objects
        self._credentials = None
        self._service = None

        # Remove token file
        if self._token_path.exists():
            try:
                self._token_path.unlink()
                logger.debug("Token file removed: %s", self._token_path)
            except Exception as e:
                raise AuthenticationError(f"Failed to remove token file: {e}") from e
