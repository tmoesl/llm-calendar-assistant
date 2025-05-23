"""
Delete Event Extractor Module

Extractor node for event deletion in the pipeline.
Extracts event details from event request using LLM call.
Pydantic response model is validated before passed to the next node in the pipeline.
"""

from typing import Any

from app.core.node import Node
from app.core.schema.task import TaskContext
from app.pipeline.schema.delete import DeleteContext, DeleteResponse
from app.services.llm_factory import LLMFactory
from app.services.log_service import logger
from app.utils.datetime_utils import get_datetime_reference


class DeleteEventExtractor(Node):
    """Extracts search criteria for event deletion"""

    def __init__(self):
        """Initialize extractor"""
        self.llm = LLMFactory("openai")
        logger.info("Initialized %s", self.node_name)

    def get_context(self, task_context: TaskContext) -> DeleteContext:
        """Extract context for deletion creation"""
        return DeleteContext(
            request=task_context.event.request, datetime_ref=get_datetime_reference()
        )

    def create_completion(self, context: DeleteContext) -> tuple[DeleteResponse, Any]:
        """Extract search criteria using LLM"""

        response_model, completion = self.llm.create_completion(
            response_model=DeleteResponse,
            messages=[
                {
                    "role": "system",
                    "content": f"""Extract relevant search criteria to identify calendar events for deletion.

                    # Current Reference Information
                    Current datetime: {context.datetime_ref.dateTime}
                    System timezone: {context.datetime_ref.timeZone}

                    # Tasks

                    1. **Time Reference Extraction (`time_window.center.dateTime`)**
                    - Identify any temporal expressions (absolute or relative) in the user's input.
                    - For relative times (e.g., "tomorrow", "next week"):
                        * Use the provided current reference time as a base.
                        * Convert to RFC3339 format.
                        * The `dateTime` string MUST include the correct timezone offset (e.g., +10:00, -07:00, +00:00) derived from the IANA `timeZone` determined in Step 2 (Timezone Selection).
                    - For absolute times (e.g., "May 5th 3pm"):
                        * Convert directly to RFC3339 format.
                        * If no timezone information can be inferred, use the system reference timezone to compute the offset.
                        * The `dateTime` string MUST include the correct offset matching the IANA time zone.
                    - Default duration is not needed, but buffer is:
                        * Specific times (e.g., "3pm"): buffer = 5 minutes.
                        * Ranges (e.g., "10am to 12pm"): use center of range, buffer = half the duration (e.g., 60 min).
                        * Broad ranges (e.g., "morning", "afternoon"): use predefined center + buffer:
                            - Morning = 10:00, buffer = 120
                            - Afternoon = 15:00, buffer = 180

                    2. **Timezone Resolution (`time_window.center.timeZone`)**
                    - Determine the timezone using the following priority:
                        1. Location keywords → map to IANA time zone (e.g., "meeting in London" → "Europe/London")
                        2. Explicit timezone names → convert to valid IANA name if necessary (e.g., "PST" → "America/Los_Angeles")
                        3. No timezone → fallback to system timezone from the reference above

                    - The determined IANA time zone MUST be used for `time_window.center.timeZone`
                    - The offset in `center.dateTime` MUST match the IANA timezone at that moment

                    3. **Fallback Reference Check**
                    - When neither location nor timezone is provided, use the reference datetime and timezone to resolve relative expressions.

                    4. **Context Terms Extraction (`context_terms`)**
                    - Extract meaningful keywords likely to appear in the event's summary, description, or location.
                    - Focus on subject matter, topics, and proper nouns (e.g., "roadmap", "planning", "Q2 sync", "London office").
                    - Do **not** include email addresses or data not used in the search query (e.g., attendee emails).
                    - Lowercase all terms and remove generic or filler words (e.g., "the", "with", "about").
                    - Prioritize words that would help identify the event via Google Calendar's free-text `q` search.

                    5. **Event ID Extraction (`event_id`)**
                    - Extract an explicit Google Calendar event ID if provided by the user.

                    6. **Compile Reasoning and Parsing Issues**
                    - Include an explanation in `reasoning` of how time and timezone were resolved.
                    - List any uncertainties, ambiguities, or assumptions made in `parsing_issues`.
                    
                    # Output Format

                    Return a Google Calendar API compatible search criteria:
                    
                    {{
                        "event_id": [optional string],
                        "time_window": {{
                            "center": {{
                            "dateTime": "2025-05-07T15:00:00+10:00",
                            "timeZone": "Australia/Sydney"
                            }},
                            "buffer_minutes": 5,
                            "original_reference": [string of original time phrase]
                        }},
                        "context_terms": [roadmap, planning, Q2, London, office],
                        "parsing_issues": [],
                        "reasoning": "Used timezone from location..."
                        }}

                    # Examples

                    Input: "Delete the event at 2PM tomorrow with John Doe about the engineering roadmap planning for 2028."  
                    Reference time: "2025-05-09T10:00:00"
                    Timezone: "Australia/Sydney"
                    Output: {{
                        "event_id": null,
                        "time_window": {{
                            "center": {{
                            "dateTime": "2025-05-10T14:00:00+10:00",
                            "timeZone": "Australia/Sydney"
                            }},
                            "buffer_minutes": 5,
                            "original_reference": "2PM tomorrow"
                        }},
                        "context_terms": ["engineering", "roadmap", "planning", "2028"],
                        "parsing_issues": [],
                        "reasoning": "Resolved '2PM tomorrow' using reference date and timezone; excluded participant names from context_terms; extracted topic keywords relevant to event search."
                        }}

                    Input: "Delete all meetings tomorrow in the morning"
                    Reference time: "2025-05-09T10:00:00+10:00"
                    Timezone: "Australia/Sydney"
                    Output: {{
                        "event_id": null,
                        "time_window": {{
                            "center": {{
                            "dateTime": "2025-05-10T10:00:00+10:00",
                            "timeZone": "Australia/Sydney"
                            }},
                            "buffer_minutes": 120,
                            "original_reference": "tomorrow morning"
                        }},
                        "context_terms": [],
                        "parsing_issues": [],
                        "reasoning": "Extracted time (3pm), resolved using provided timezone; no relevant context available."
                        }}


                    # Notes

                    - If no location or timezone is provided, use the system's current datetime and timezone as reference.
                    - All `timeZone` values must be valid IANA names (e.g., "Europe/London", "Australia/Sydney").
                    - All `dateTime` values must follow RFC3339 format and include the correct UTC offset.
                    - The `dateTime` offset MUST correspond to the specified IANA `timeZone` at that moment in time.
                    - Only populate fields that can be inferred from the input; leave others null.
                    - Clearly document any parsing assumptions or ambiguities in `parsing_issues`.
                    - Always include a `reasoning` field explaining the logic used to resolve time and timezone.
                    """,
                },
                {"role": "user", "content": context.request},
            ],
        )

        return response_model, completion

    def process(self, task_context: TaskContext) -> TaskContext:
        """Process deletion criteria extraction"""
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

        except Exception as e:
            logger.error("Failed to extract deletion criteria: %s", str(e))
            task_context.nodes[self.node_name] = {"status": "error", "error": str(e)}

        return task_context

    def _log_results(self, response: DeleteResponse):
        """Log extraction results"""
        # Log primary search criteria
        if response.event_id:
            logger.info("Extracted deletion criteria (event_id: %s)", response.event_id)
        else:
            logger.info(
                "Extracted deletion criteria (window: %s, context terms: %s)",
                response.time_window.original_reference if response.time_window else None,
                ", ".join(response.context_terms) if response.context_terms else None,
            )

        # Log any issues and reasoning
        if response.parsing_issues:
            logger.debug("Parsing issues: %s", ", ".join(response.parsing_issues))
        logger.debug("Extraction reasoning: %s", response.reasoning)
