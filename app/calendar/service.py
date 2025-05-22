"""
Google Calendar Service Module

Handles calendar operations using the Google Calendar API.
"""

from typing import Any

from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError

from app.services.log_service import logger


class GoogleCalendarService:
    """Performs Google Calendar API operations using an authenticated service."""

    def __init__(self, service: Resource):
        """
        Initialize with an authenticated service object.

        Args:
            service: Authenticated googleapiclient.discovery.Resource object
        Raises:
            ValueError: If service object is not provided
        """
        if not service:
            raise ValueError("Authenticated service object is required")
        self.service = service
        logger.info("Initialized Google Calendar service")

    def create_event(self, calendar_id: str, event_body: dict) -> dict:
        """
        Create a calendar event.

        Args:
            calendar_id: Target calendar ID (e.g., 'primary')
            event_body: Event resource dictionary

        Returns:
            Created event resource

        Raises:
            ValueError: If required parameters are missing
            HttpError: If the API call fails
        """
        if not calendar_id or not event_body:
            raise ValueError("Calendar ID and event body are required")

        try:
            created_event = (
                self.service.events().insert(calendarId=calendar_id, body=event_body).execute()  # type: ignore
            )

            logger.info("Created event: %s", created_event.get("htmlLink"))
            return created_event

        except HttpError as error:
            logger.error("API error creating event: %s", error)
            raise
        except Exception as e:
            logger.error("Unexpected error creating event: %s", e)
            raise

    def delete_event(self, calendar_id: str, event_id: str, **query_params: Any) -> None:
        """
        Delete a calendar event.

        Args:
            calendar_id: Calendar containing the event (path parameter)
            event_id: Event to delete (path parameter)
            **query_params: Query parameters (GoogleDeleteEventRequest)

        Raises:
            ValueError: If required parameters are missing
            HttpError: If the API call fails
        """
        if not calendar_id or not event_id:
            raise ValueError("Calendar ID and Event ID are required")

        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id,
                **query_params,
            ).execute()  # type: ignore

            logger.info("Deleted event %s from calendar %s", event_id, calendar_id)

        except HttpError as error:
            if error.resp.status == 404:
                logger.warning("Event %s not found (already deleted?)", event_id)
                return
            logger.error("API error deleting event: %s", error)
            raise
        except Exception as e:
            logger.error("Unexpected error deleting event: %s", e)
            raise

    def list_events(
        self,
        calendar_id: str = "primary",
        **query_params: Any,
    ) -> list[dict]:
        """
        List events from a calendar.

        Args:
            calendar_id: Target calendar ID (path parameter)
            **query_params: Query parameters from GoogleLookupEventRequest including:
                - timeMin: Start time (RFC3339)
                - timeMax: End time (RFC3339)
                - timeZone: IANA timezone
                - q: Free text search
                - singleEvents: Whether to expand recurring events (default: True)
                - orderBy: Sort order (default: "startTime")
                - maxResults: Maximum events to return (default: 10)

        Returns:
            List of event resources

        Raises:
            HttpError: If the API call fails
        """
        try:
            events_result = (
                self.service.events()  # type: ignore
                .list(
                    calendarId=calendar_id,
                    **query_params,
                )
                .execute()
            )

            events = events_result.get("items", [])
            logger.info("Listed %d events from calendar %s", len(events), calendar_id)
            return events

        except HttpError as error:
            logger.error("API error listing events: %s", error)
            raise
        except Exception as e:
            logger.error("Unexpected error listing events: %s", e)
            raise

    def get_event(self, calendar_id: str, event_id: str) -> dict:
        """
        Get a specific calendar event by ID.

        Args:
            calendar_id: Calendar containing the event (path parameter)
            event_id: Event ID to retrieve (path parameter)

        Returns:
            Event resource dictionary

        Raises:
            ValueError: If required parameters are missing
            HttpError: If the API call fails
        """
        if not calendar_id or not event_id:
            raise ValueError("Calendar ID and Event ID are required")

        try:
            event = (
                self.service.events().get(calendarId=calendar_id, eventId=event_id).execute()  # type: ignore
            )

            logger.info("Retrieved event: %s", event.get("htmlLink"))
            return event

        except HttpError as error:
            logger.error("API error retrieving event: %s", error)
            raise
        except Exception as e:
            logger.error("Unexpected error retrieving event: %s", e)
            raise
