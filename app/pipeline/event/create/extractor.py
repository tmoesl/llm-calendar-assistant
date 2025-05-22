"""
Create Event Extractor Module

Extractor node for event creation in the pipeline.
Extracts event details from event request using LLM call.
Pydantic response model is validated before passed to the next node in the pipeline.
"""

from typing import Any

from pydantic import BaseModel, Field, ValidationError

from app.core.node import Node
from app.core.schema.llm import LlmCreateEvent
from app.core.schema.task import TaskContext
from app.services.llm_factory import LLMFactory
from app.services.log_service import logger
from app.utils.datetime_utils import get_datetime_reference


class CreateEventExtractor(Node):
    """Extracts and normalizes details for event creation"""

    def __init__(self):
        """Initialize extractor with configuration"""
        self.llm = LLMFactory("openai")
        logger.info("Initialized %s", self.node_name)

    class ContextModel(BaseModel):
        """Input context for event extraction"""

        user_input: str = Field(description="Original calendar request from user")
        datetime_ref: dict = Field(description="Current datetime and timezone reference")

    class ResponseModel(LlmCreateEvent):
        """Inherits from LlmCreateEvent"""

    def get_context(self, task_context: TaskContext) -> ContextModel:
        """Extract context for event creation"""
        return self.ContextModel(
            user_input=task_context.event.request, datetime_ref=get_datetime_reference()
        )

    def create_completion(self, context: ContextModel) -> tuple[ResponseModel, Any]:
        """Extract and normalize event details using LLM with upfront datetime reference"""

        response_model, completion = self.llm.create_completion(
            response_model=self.ResponseModel,
            messages=[
                {
                    "role": "system",
                    "content": f"""Extract and normalize calendar event details into Google Calendar API format.

                    # Current Reference Information
                    Current datetime: {context.datetime_ref["current_datetime"]}
                    System timezone: {context.datetime_ref["timezone"]}

                    # Tasks

                    1. **Event Title & Description**
                    - Extract a clear, concise title
                    - Include key topics/agenda in description if provided
                    
                    2. **Time Processing** (Generates `start.dateTime` and `end.dateTime`)
                    - For relative times ("tomorrow", "next week"):
                        * Use the current reference time above as base.
                        * Convert to RFC3339 format.
                        * The `dateTime` string MUST include the correct timezone offset (e.g., +10:00, -07:00, +00:00) derived from the IANA `timeZone` determined in Step 2 (Timezone Selection).
                    - For absolute times ("May 5th 3pm"):
                        * Convert directly to RFC3339 format. The `dateTime` string MUST include the correct timezone offset derived from the IANA `timeZone` determined in Step 3 (Timezone Selection).
                        * If no timezone information can be inferred for an absolute time, use the system's reference timezone (see Step 3) to calculate the offset.
                    - Default to 1 hour duration if not specified.
                    
                    3. **Timezone Selection** (Determines `start.timeZone` and `end.timeZone`)
                    - Determine the timezone using the following priority:
                        1. Location keywords → map to IANA time zone (e.g., "meeting in London" → "Europe/London")
                        2. Explicit timezone names → convert to valid IANA name if necessary (e.g., "PST" → "America/Los_Angeles")
                        3. No timezone → fallback to system timezone from the reference above

                    - The determined IANA `timeZone` MUST be used for both the `start.timeZone` and `end.timeZone` fields.
                    - The offset in the `dateTime` string MUST match the IANA timezone at that exact moment.

                    4. **Attendee Formatting**
                    - Convert names/groups to email format
                    - Use name@aiengineering.com pattern
                    
                    # Output Format

                    Return a Google Calendar API compatible event:
                    {{
                        "summary": "Team Meeting",
                        "start": {{
                            "dateTime": "2025-05-07T15:00:00+10:00",
                            "timeZone": "Australia/Sydney"
                        }},
                        "end": {{
                            "dateTime": "2025-05-07T16:00:00+10:00",
                            "timeZone": "Australia/Sydney"
                        }},
                        "description": "Monthly team sync",
                        "location": "Conference Room A",
                        "attendees": [
                            {{"email": "person@aiengineering.com"}}
                        ],
                        "parsing_issues": [],
                        "reasoning": "Used timezone from location..."
                    }}

                    # Examples

                    Input: "Schedule team meeting tomorrow at 3pm"
                    Output: {{
                        "summary": "Team Meeting",
                        "start": {{"dateTime": "2025-05-07T15:00:00+10:00", "timeZone": "Australia/Sydney"}},
                        "end": {{"dateTime": "2025-05-07T16:00:00+10:00", "timeZone": "Australia/Sydney"}},
                        "parsing_issues": [],
                        "reasoning": "Used reference time to resolve 'tomorrow' and system timezone as none specified"
                    }}

                    Input: "Set up call at 2pm London time with marketing"
                    Output: {{
                        "summary": "Marketing Call",
                        "start": {{"dateTime": "2025-05-06T14:00:00+01:00", "timeZone": "Europe/London"}},
                        "end": {{"dateTime": "2025-05-06T15:00:00+01:00", "timeZone": "Europe/London"}},
                        "attendees": [{{"email": "marketing@aiengineering.com"}}],
                        "parsing_issues": [],
                        "reasoning": "Used explicit London timezone, converted marketing to email format"
                    }}

                    # Notes

                    - If no location or timezone is provided, use the system's current datetime and timezone as reference.
                    - All `timeZone` values must be valid IANA names (e.g., "Europe/London", "Australia/Sydney").
                    - All `dateTime` values must follow RFC3339 format and include the correct UTC offset.
                    - The `dateTime` offset MUST correspond to the specified IANA `timeZone` at that moment in time.
                    - The `start.timeZone` and `end.timeZone` fields MUST be identical for a given event.
                    - Default to a 1-hour duration if no end time is specified.
                    - Only populate fields that can be inferred from the input; leave others null.
                    - Ensure `end` is after `start`.
                    - Clearly document any parsing assumptions or ambiguities in `parsing_issues`.
                    - Always include a `reasoning` field explaining the logic used to resolve time and timezone.

                    """,
                },
                {"role": "user", "content": context.user_input},
            ],
        )

        return response_model, completion

    def process(self, task_context: TaskContext) -> TaskContext:
        """Process event extraction and normalization"""
        try:
            context = self.get_context(task_context)
            response_model, completion = self.create_completion(context)

            # Store results
            task_context.nodes[self.node_name] = {
                "response_model": response_model,
                "usage": completion.usage,
                "status": "success",
            }

            self._log_results(response_model)

        except ValidationError as ve:
            logger.error("Event data validation error: %s", str(ve))
            task_context.nodes[self.node_name] = {"status": "error", "error": str(ve)}
        except Exception as e:
            logger.error("Extraction error: %s", str(e))
            task_context.nodes[self.node_name] = {"status": "error", "error": str(e)}

        return task_context

    def _log_results(self, response: ResponseModel):
        """Log extraction results"""
        logger.info("Extracted event details: '%s'", response.summary)
        if response.parsing_issues:
            logger.debug("Parsing issues: %s", ", ".join(response.parsing_issues))
        logger.debug("Extraction reasoning: %s", response.reasoning)
