"""
Classification Module

Node for event classification in the pipeline.
Classifies the type of event requested.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from app.config.settings import get_settings
from app.core.node import Node
from app.core.schema.task import TaskContext
from app.services.llm_factory import LLMFactory
from app.services.log_service import logger


class EventType(str, Enum):
    """Enum for event types"""

    CREATE_EVENT = "create_event"
    UPDATE_EVENT = "update_event"
    DELETE_EVENT = "delete_event"
    VIEW_EVENT = "view_event"


class ClassifyEvent(Node):
    """Classifies the type of calendar event requested"""

    def __init__(self):
        """Initialize classifier with configuration"""
        settings = get_settings()
        self.confidence_threshold = settings.app.confidence_threshold
        self.llm = LLMFactory("openai")
        logger.info("Initialized %s", self.node_name)

    class ContextModel(BaseModel):
        """Input context for intent classification"""

        user_input: str = Field(description="Original calendar request from user")

    class ResponseModel(BaseModel):
        """LLM response for intent classification"""

        # Intent classification
        has_intent: bool = Field(description="Whether a clear calendar intent was detected")
        request_type: EventType | None = Field(
            default=None, description="Classified intent type if clear intent detected"
        )

        # Assessment details
        confidence_score: float = Field(
            ge=0.0, le=1.0, description="Confidence in intent classification"
        )
        reasoning: str = Field(description="Detailed explanation of classification results")

    def get_context(self, task_context: TaskContext) -> ContextModel:
        """Extract context for intent classification"""
        return self.ContextModel(user_input=task_context.event.request)

    def create_completion(self, context: ContextModel) -> tuple[ResponseModel, Any]:
        """Get validation results from LLM"""
        response_model, completion = self.llm.create_completion(
            response_model=self.ResponseModel,
            messages=[
                {
                    "role": "system",
                    "content": """Analyze the calendar request and classify its intent using the following structured steps.

                    # Steps

                    1. **Intent Detection**
                    - **Action Words**: Identify whether the input contains specific action words such as 'create', 'schedule', 'add', 'update', 'modify', 'change', 'reschedule', 'delete', 'cancel', 'remove', 'view', 'show', or 'check'.
                    - **Intent Presence**: If no recognizable action word is found, set `has_intent=false` and explain the absence of a clear intent.
                    - **Phrasing Recognition**: Recognize implicit or indirect phrases that imply intent. Treat "show me", "what's on", "do I have anything", "pull up", "see what's coming up", or "look at my calendar" as **view/event** if they reference timeframes or calendars.
                    - **Connection to Event**: For all intents, ensure they connect to an actual meeting/event/entry. If ambiguous, provide details on the connection or explain the ambiguity.
                    - Proceed to classification only if an intent is detected.

                    2. **Intent Classification**
                    - Classify the intent using the following mapping:
                    - **'create_event'**: Detected action words like create, schedule, add, or new.
                    - **'update_event'**: Detected action words like update, modify, change, reschedule.
                    - **'delete_event'**: Detected action words like delete, remove, or cancel.
                    - **'view_event'**: Detected action words like view, show, display, or check.

                    3. **Reasoning and Confidence**
                    - **Reasoning**: Clearly explain why the intent was assigned to the given category, referencing specific terms or patterns found in the input.
                    - **Confidence Score**: Provide a numeric value between 0.0 and 1.0 indicating the overall confidence in the classification based on clarity and presence of intent signals.

                    # Output Format

                    Please return a structured JSON object in the following format:

                    {
                    "request_type": "<one of: create_event, update_event, delete_event, view_event>",
                    "has_intent": true | false,
                    "reasoning": "<brief explanation of classification or why no intent was found>",
                    "confidence_score": 0.0 – 1.0,
                    }

                    ### Field Descriptions

                    - **request_type**: A string classification of the identified intent (only included if `has_intent=true`).
                    - **has_intent**: Boolean indicating whether an actionable intent was identified.
                    - **reasoning**: Clear explanation for how the classification was made, or why no classification was possible.
                    - **confidence_score**: A float between 0.0 and 1.0 representing the model's confidence in the classification.

                    # Examples

                    - **Input**: "Schedule meeting with Sarah next Monday"
                    - **Output**:
                        {
                        "request_type": "create_event",
                        "has_intent": true,
                        "reasoning": "Detected the word 'schedule', which maps to a create intent.",
                        "confidence_score": 0.9
                        }

                    - **Input**: "calendar please"
                    - **Output**:
                        {
                        "has_intent": false,
                        "reasoning": "No identifiable action word or intent found in input.",
                        "confidence_score": 0.2
                        }
                    
                    - **Input**: "Can you pencil me in for an appointment on Thursday?"
                    - **Output**:
                        {
                        "request_type": "create_event",
                        "has_intent": true,
                        "reasoning": "The phrase 'pencil me in' implies a create event intent.",
                        "confidence_score": 0.8
                        }


                    - **Input**: "Remove my 3 PM meeting tomorrow."
                    - **Output**:
                        {
                        "request_type": "delete_event",
                        "has_intent": true,
                        "reasoning": "The word 'remove' indicates a delete event intent.",
                        "confidence_score": 0.9
                        }

                    - **Input**: "Show me my calendar for next week"
                    - **Output**:
                    {
                        "request_type": "view_event",
                        "has_intent": true,
                        "reasoning": "Detected the phrase 'Show me', which maps to a view intent.",
                        "confidence_score": 0.85
                        }
                        
                    # Notes

                    - Carefully distinguish synonyms or ambiguous verbs that may signal different types of intent.
                    - Consider idiomatic or indirect phrasing that may imply an intent (e.g., 'put something in my calendar' → create).
                    - Use reasoning to explain ambiguous cases and maintain transparency in classification decisions.
                    """,
                },
                {"role": "user", "content": context.user_input},
            ],
        )
        return response_model, completion

    def process(self, task_context: TaskContext) -> TaskContext:
        """Process intent classification"""
        try:
            context = self.get_context(task_context)
            response_model, completion = self.create_completion(context)

            # Core validation check
            is_classified = (
                response_model.has_intent
                and response_model.request_type is not None
                and response_model.confidence_score >= self.confidence_threshold
            )

            # Store results
            task_context.nodes[self.node_name] = {
                "response_model": response_model,
                "usage": completion.usage,
                "status": "blocked" if not is_classified else "success",
                "details": {
                    "has_intent": response_model.has_intent,
                    "intent_type": response_model.request_type,
                    "confidence": response_model.confidence_score,
                    "reasoning": response_model.reasoning,
                },
            }

            self._log_classification_results(is_classified, response_model)

        except ValidationError as ve:
            logger.error("Validation error: %s", str(ve))
            task_context.nodes[self.node_name] = {"status": "error", "error": str(ve)}

        except Exception as e:
            logger.error("Unexpected error in validation: %s", str(e))
            task_context.nodes[self.node_name] = {"status": "error", "error": str(e)}

        return task_context

    def _log_classification_results(self, is_valid: bool, response: ResponseModel):
        """Log classification results with summary and details"""
        if is_valid:
            logger.info(
                "Intent classified as '%s' (confidence: %.2f)",
                response.request_type.value if response.request_type else None,
                response.confidence_score,
            )
            return

        # Collect failed classification types
        failures = []
        if not response.has_intent:
            failures.append("invalid intent")
        if response.confidence_score < self.confidence_threshold:
            failures.append("low confidence")

        # Log summary at INFO level
        logger.info("Classification failed (%s)", ", ".join(failures))

        # Log details at DEBUG level
        logger.debug(
            "Classification details: %s (confidence: %.2f)",
            response.reasoning,
            response.confidence_score,
        )
