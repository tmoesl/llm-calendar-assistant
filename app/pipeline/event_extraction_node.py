"""
Event extraction node for the pipeline.
Extracts raw event information from user input.
"""

from app.llm.processor import extract_raw_event_data
from app.models.schemas import TaskEvent
from app.services.log_setup import logger

from .base_node import BaseNode


class EventExtractionNode(BaseNode):
    """Extracts raw calendar event information from user input"""

    def process(self, task: TaskEvent) -> TaskEvent:
        """
        Extract raw event information from the user input

        Args:
            task: TaskEvent containing user input to process

        Returns:
            TaskEvent with extracted raw event data and updated status
        """
        extracted = extract_raw_event_data(task.user_input)

        task.metadata["extraction"] = {
            "confidence": extracted.extraction_confidence,
            "parsing_notes": extracted.parsing_notes,
            "fields_found": [
                field
                for field, value in extracted.model_dump().items()
                if value is not None
                and field not in ["extraction_confidence", "parsing_notes"]
            ],
            "timestamp": task.timestamp,
        }

        # Store raw extracted data for validation node
        task.metadata["raw_event_data"] = extracted.model_dump()

        if extracted.extraction_confidence < 0.5:  # Very low confidence threshold
            logger.warning(
                "Low confidence in event extraction (%.2f)",
                extracted.extraction_confidence,
            )
            task.status = "extraction_failed"
            return task

        logger.info(
            "Event details extracted (confidence: %.2f, fields: %s)",
            extracted.extraction_confidence,
            ", ".join(task.metadata["extraction"]["fields_found"]),
        )

        task.status = "extraction_completed"
        return task
