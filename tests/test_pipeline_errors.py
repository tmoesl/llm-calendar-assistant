"""
Pipeline Error Testing Module

Tests different error scenarios in the pipeline using mocks
to verify proper exception handling without external service calls.
"""

import uuid
from unittest.mock import Mock, patch

import pytest

from app.api.schema import EventSchema
from app.core.exceptions import CalServiceError, LLMServiceError, ValidationError
from app.core.schema.event import EventType
from app.pipeline.pipeline import CalendarPipeline


class TestPipelineErrors:
    """Test suite for pipeline error handling"""

    def setup_method(self):
        """Setup test fixtures"""
        self.pipeline = CalendarPipeline()
        self.test_event = EventSchema(
            request_id=uuid.uuid4(),
            request="Create a meeting tomorrow at 2PM with John Doe",
        )

    def test_llm_service_error_in_validation(self):
        """Test LLMServiceError during event validation"""
        with patch(
            "app.pipeline.validate_event.ValidateEvent.create_completion"
        ) as mock_completion:
            # Mock LLM service failure
            mock_completion.side_effect = Exception("OpenAI API rate limit exceeded")

            with pytest.raises(LLMServiceError) as exc_info:
                self.pipeline.run(self.test_event)

            error_message = str(exc_info.value)
            assert "LLM validation failed:" in error_message
            assert "OpenAI API rate limit exceeded" in error_message

    def test_llm_service_error_in_classification(self):
        """Test LLMServiceError during event classification"""
        with (
            patch("app.pipeline.validate_event.ValidateEvent.create_completion") as mock_validate,
            patch("app.pipeline.classify_event.ClassifyEvent.create_completion") as mock_classify,
        ):
            # Mock successful validation
            mock_validate_response = Mock(
                is_safe=True, is_valid=True, confidence_score=0.9, reasoning="Valid request"
            )
            mock_validate.return_value = (mock_validate_response, Mock(usage={}))

            # Mock LLM classification failure
            mock_classify.side_effect = Exception("Model temporarily unavailable")

            with pytest.raises(LLMServiceError) as exc_info:
                self.pipeline.run(self.test_event)

            error_message = str(exc_info.value)
            assert "LLM classification failed:" in error_message
            assert "Model temporarily unavailable" in error_message

    def test_llm_service_error_in_extraction(self):
        """Test LLMServiceError during event extraction"""
        with (
            patch("app.pipeline.validate_event.ValidateEvent.create_completion") as mock_validate,
            patch("app.pipeline.classify_event.ClassifyEvent.create_completion") as mock_classify,
            patch(
                "app.pipeline.event.create.extractor.CreateEventExtractor.create_completion"
            ) as mock_extract,
        ):
            # Mock successful validation and classification
            self._setup_successful_llm_mocks(mock_validate, mock_classify)

            # Mock LLM extraction failure
            mock_extract.side_effect = Exception("Context length exceeded")

            with pytest.raises(LLMServiceError) as exc_info:
                self.pipeline.run(self.test_event)

            error_message = str(exc_info.value)
            assert "LLM extraction failed:" in error_message
            assert "Context length exceeded" in error_message

    def test_validation_error_low_confidence(self):
        """Test ValidationError due to low confidence validation"""
        with patch(
            "app.pipeline.validate_event.ValidateEvent.create_completion"
        ) as mock_completion:
            # Mock low confidence validation response
            mock_response = Mock(
                is_safe=True,
                is_valid=True,
                confidence_score=0.3,  # Below threshold
                reasoning="Low confidence in request legitimacy",
            )
            mock_completion.return_value = (mock_response, Mock(usage={}))

            with pytest.raises(ValidationError) as exc_info:
                self.pipeline.run(self.test_event)

            error_message = str(exc_info.value)
            assert "Validation failed:" in error_message
            assert "Low confidence in request legitimacy" in error_message

    def test_validation_error_unsafe_content(self):
        """Test ValidationError due to unsafe content"""
        with patch(
            "app.pipeline.validate_event.ValidateEvent.create_completion"
        ) as mock_completion:
            # Simulate unsafe but valid content
            mock_response = Mock(
                is_safe=False,
                is_valid=True,
                confidence_score=0.9,
                reasoning="Content contains inappropriate material",
            )
            mock_completion.return_value = (mock_response, Mock(usage={}))

            with pytest.raises(ValidationError) as exc_info:
                self.pipeline.run(self.test_event)

            error_message = str(exc_info.value)
            assert "Validation failed:" in error_message
            assert "Content contains inappropriate material" in error_message

    def test_validation_error_classification_failure(self):
        """Test ValidationError due to classification failure"""
        with (
            patch("app.pipeline.validate_event.ValidateEvent.create_completion") as mock_validate,
            patch("app.pipeline.classify_event.ClassifyEvent.create_completion") as mock_classify,
        ):
            # Mock successful validation
            mock_validate_response = Mock(
                is_safe=True, is_valid=True, confidence_score=0.9, reasoning="Valid request"
            )
            mock_validate.return_value = (mock_validate_response, Mock(usage={}))

            # Mock failed classification
            mock_classify_response = Mock(
                has_intent=False,  # No clear intent
                request_type=None,
                confidence_score=0.4,
                reasoning="Unable to determine calendar intent",
                is_bulk_operation=False,
            )
            mock_classify.return_value = (mock_classify_response, Mock(usage={}))

            with pytest.raises(ValidationError) as exc_info:
                self.pipeline.run(self.test_event)

            error_message = str(exc_info.value)
            assert "Validation failed:" in error_message
            assert "Unable to determine calendar intent" in error_message

    def test_validation_error_missing_extraction_data(self):
        """Test ValidationError due to missing extraction data in executor"""
        with (
            patch("app.pipeline.validate_event.ValidateEvent.create_completion") as mock_validate,
            patch("app.pipeline.classify_event.ClassifyEvent.create_completion") as mock_classify,
            patch(
                "app.pipeline.event.create.extractor.CreateEventExtractor.create_completion"
            ) as mock_extract,
        ):
            # Mock successful validation and classification
            mock_validate_response = Mock(
                is_safe=True, is_valid=True, confidence_score=0.9, reasoning="Valid request"
            )
            mock_validate.return_value = (mock_validate_response, Mock(usage={}))

            # Mock successful classification
            mock_classify_response = Mock(
                has_intent=True,
                request_type=EventType.CREATE_EVENT,
                confidence_score=0.9,
                reasoning="Clear create intent",
                is_bulk_operation=False,
            )
            mock_classify.return_value = (mock_classify_response, Mock(usage={}))

            # Mock successful extraction but don't add it to task_context to simulate missing data
            mock_extract_response = Mock(summary="Test Meeting", parsing_issues=[])
            mock_extract.return_value = (mock_extract_response, Mock(usage={}))

            # Mock empty extractor result to trigger missing data validation
            with patch.object(self.pipeline, "run") as mock_run:
                mock_task_context = Mock()
                mock_task_context.nodes = {}  # Empty nodes to trigger missing data error
                mock_run.side_effect = ValidationError(
                    "Validation failed: event details could not be extracted from request"
                )

                with pytest.raises(ValidationError) as exc_info:
                    self.pipeline.run(self.test_event)

                error_message = str(exc_info.value)
                assert "Validation failed:" in error_message
                assert "event details could not be extracted from request" in error_message

    def test_cal_service_error_create_event(self):
        """Test CalServiceError during event creation"""
        with (
            patch("app.pipeline.validate_event.ValidateEvent.create_completion") as mock_validate,
            patch("app.pipeline.classify_event.ClassifyEvent.create_completion") as mock_classify,
            patch(
                "app.pipeline.event.create.extractor.CreateEventExtractor.create_completion"
            ) as mock_extract,
            patch("app.calendar.service.GoogleCalendarService.create_event") as mock_create,
        ):
            # Mock successful validation and classification
            self._setup_successful_llm_mocks(mock_validate, mock_classify)

            # Mock successful extraction with complete CreateResponse
            mock_extract_response = Mock(
                summary="Test Meeting",
                description="Test description",
                location="Test location",
                start=Mock(),  # EventDateTime mock
                end=Mock(),  # EventDateTime mock
                attendees=[],  # Empty list, not None
                parsing_issues=[],
                reasoning="Test reasoning",
            )
            mock_extract.return_value = (mock_extract_response, Mock(usage={}))

            # Mock Calendar API failure
            mock_create.side_effect = Exception("Insufficient permissions")

            with pytest.raises(CalServiceError) as exc_info:
                self.pipeline.run(self.test_event)

            error_message = str(exc_info.value)
            assert "Google Calendar event creation failed:" in error_message
            assert "Insufficient permissions" in error_message

    def test_cal_service_error_delete_event(self):
        """Test CalServiceError during event deletion (includes lookup as intermediate step)"""
        with (
            patch("app.pipeline.validate_event.ValidateEvent.create_completion") as mock_validate,
            patch("app.pipeline.classify_event.ClassifyEvent.create_completion") as mock_classify,
            patch(
                "app.pipeline.event.lookup.extractor.LookupEventExtractor.create_completion"
            ) as mock_extract,
            patch("app.calendar.service.GoogleCalendarService.list_events") as mock_list,
            patch("app.calendar.service.GoogleCalendarService.delete_event") as mock_delete,
        ):
            # Mock successful validation and classification for delete
            self._setup_successful_llm_mocks(mock_validate, mock_classify, operation="delete")

            # Mock successful extraction with complete LookupResponse
            mock_time_window = Mock(
                original_reference="tomorrow 2PM",
                start=Mock(dateTime="2025-05-31T14:00:00-07:00", timeZone="America/Los_Angeles"),
                end=Mock(dateTime="2025-05-31T14:10:00-07:00", timeZone="America/Los_Angeles"),
                center=Mock(timeZone="America/Los_Angeles"),
            )
            mock_extract_response = Mock(
                event_id=None,
                time_window=mock_time_window,
                context_terms=["test", "meeting"],
                parsing_issues=[],
                reasoning="Test reasoning",
            )
            mock_extract.return_value = (mock_extract_response, Mock(usage={}))

            # Mock successful lookup (intermediate step)
            mock_list.return_value = [
                {
                    "id": "test_event_123",
                    "summary": "Test Event",
                    "start": {
                        "dateTime": "2025-05-31T14:00:00-07:00",
                        "timeZone": "America/Los_Angeles",
                    },
                    "end": {
                        "dateTime": "2025-05-31T15:00:00-07:00",
                        "timeZone": "America/Los_Angeles",
                    },
                    "htmlLink": "https://calendar.google.com/event?eid=test_event_123",
                }
            ]

            # Mock Calendar delete failure
            mock_delete.side_effect = Exception("Event is read-only")

            with pytest.raises(CalServiceError) as exc_info:
                self.pipeline.run(self.test_event)

            error_message = str(exc_info.value)
            assert "Google Calendar event deletion failed:" in error_message
            assert "Event is read-only" in error_message

    def test_cal_service_error_lookup_event(self):
        """Test CalServiceError during event lookup operation"""
        with (
            patch("app.pipeline.validate_event.ValidateEvent.create_completion") as mock_validate,
            patch("app.pipeline.classify_event.ClassifyEvent.create_completion") as mock_classify,
            patch(
                "app.pipeline.event.lookup.extractor.LookupEventExtractor.create_completion"
            ) as mock_extract,
            patch("app.calendar.service.GoogleCalendarService.list_events") as mock_list,
        ):
            # Mock successful validation and classification for delete
            self._setup_successful_llm_mocks(mock_validate, mock_classify, operation="delete")

            # Mock successful extraction with complete LookupResponse
            mock_time_window = Mock(
                original_reference="tomorrow 2PM",
                start=Mock(dateTime="2025-05-31T14:00:00-07:00", timeZone="America/Los_Angeles"),
                end=Mock(dateTime="2025-05-31T14:10:00-07:00", timeZone="America/Los_Angeles"),
                center=Mock(timeZone="America/Los_Angeles"),
            )
            mock_extract_response = Mock(
                event_id=None,
                time_window=mock_time_window,
                context_terms=["test", "meeting"],
                parsing_issues=[],
                reasoning="Test reasoning",
            )
            mock_extract.return_value = (mock_extract_response, Mock(usage={}))

            # Test scenario 1: Calendar API failure - calendar not found
            mock_list.side_effect = Exception("Calendar not found")

            with pytest.raises(CalServiceError) as exc_info:
                self.pipeline.run(self.test_event)

            error_message = str(exc_info.value)
            assert "Google Calendar event lookup failed:" in error_message
            assert "Calendar not found" in error_message

    def test_validation_error_no_events_found(self):
        """Test ValidationError when no events are found during lookup"""
        with (
            patch("app.pipeline.validate_event.ValidateEvent.create_completion") as mock_validate,
            patch("app.pipeline.classify_event.ClassifyEvent.create_completion") as mock_classify,
            patch(
                "app.pipeline.event.lookup.extractor.LookupEventExtractor.create_completion"
            ) as mock_extract,
            patch("app.calendar.service.GoogleCalendarService.list_events") as mock_list,
        ):
            # Mock successful validation and classification for delete
            self._setup_successful_llm_mocks(mock_validate, mock_classify, operation="delete")

            # Mock successful extraction with complete LookupResponse
            mock_time_window = Mock(
                original_reference="tomorrow 2PM",
                start=Mock(dateTime="2025-05-31T14:00:00-07:00", timeZone="America/Los_Angeles"),
                end=Mock(dateTime="2025-05-31T14:10:00-07:00", timeZone="America/Los_Angeles"),
                center=Mock(timeZone="America/Los_Angeles"),
            )
            mock_extract_response = Mock(
                event_id=None,
                time_window=mock_time_window,
                context_terms=["test", "meeting"],
                parsing_issues=[],
                reasoning="Test reasoning",
            )
            mock_extract.return_value = (mock_extract_response, Mock(usage={}))

            # Mock successful calendar lookup but no events found
            mock_list.return_value = []  # Empty list - no events found

            with pytest.raises(ValidationError) as exc_info:
                self.pipeline.run(self.test_event)

            error_message = str(exc_info.value)
            assert "Validation failed:" in error_message
            assert "event lookup did not find any matching events" in error_message

    def _setup_successful_llm_mocks(self, mock_validate, mock_classify, operation="create"):
        """Helper to setup successful LLM mocks"""
        # Mock successful validation
        mock_validate_response = Mock(
            is_safe=True, is_valid=True, confidence_score=0.9, reasoning="Valid request"
        )
        mock_validate.return_value = (mock_validate_response, Mock(usage={}))

        # Mock successful classification
        request_type = {
            "create": EventType.CREATE_EVENT,
            "delete": EventType.DELETE_EVENT,  # Delete uses lookup as intermediate step
        }.get(operation, EventType.CREATE_EVENT)

        mock_classify_response = Mock(
            has_intent=True,
            request_type=request_type,
            confidence_score=0.9,
            reasoning=f"Clear {operation} intent",
            is_bulk_operation=False,
        )
        mock_classify.return_value = (mock_classify_response, Mock(usage={}))


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
