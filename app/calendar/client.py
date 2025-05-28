"""
Google Calendar API Client Module
Handles initialization and authentication of Google Calendar service.
"""

import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the API scope for full calendar access (read/write)
SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GoogleCalendarClient:
    """Google Calendar API client with authentication handling"""

    def __init__(self, token_path: str = "token.json", creds_path: str = "credentials.json"):
        self.token_path = token_path
        self.creds_path = creds_path
        self.credentials: Credentials | None = None
        self.service = None

    def authenticate(self):
        """Handle authentication flow"""
        # Only authenticate if service is not already initialized
        if self.service is not None:
            return

        # Check for existing credentials
        if os.path.exists(self.token_path):
            self.credentials = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        # If no valid credentials are available, prompt the user to log in.
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.creds_path, SCOPES)
                self.credentials = flow.run_local_server(port=0)

        # Save credentials for future runs
        if self.credentials:
            with open(self.token_path, "w", encoding="utf-8") as token:
                token.write(self.credentials.to_json())

        # Check if valid credentials are available
        if not self.credentials or not self.credentials.valid:
            raise ValueError("Invalid credentials. Please check your authentication flow.")

        # Build the service object
        self.service = build("calendar", "v3", credentials=self.credentials)

    def create_event(self, calendar_id: str, event: dict) -> dict:
        """Create a calendar event"""
        self.authenticate()

        if self.service is None:
            raise ValueError("Failed to initialize Google Calendar service")

        return self.service.events().insert(calendarId=calendar_id, body=event).execute()
