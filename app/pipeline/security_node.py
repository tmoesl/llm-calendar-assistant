"""
Security validation node for the pipeline.
Validates user input for potential security concerns.
"""

from app.llm.processor import security_check
from app.models.schemas import TaskEvent

from .base_node import BaseNode


class SecurityNode(BaseNode):
    """Validates input for security concerns"""

    def process(self, task: TaskEvent) -> TaskEvent:
        """
        Process security validation on the user input

        Args:
            task: TaskEvent containing user input to validate

        Returns:
            TaskEvent with updated security metadata and status
        """
        security_result = security_check(task.user_input)

        task.metadata["security"] = {
            "is_safe": security_result.is_safe,
            "risk_flags": security_result.risk_flags,
            "timestamp": task.timestamp,
        }

        task.status = "security_checked"
        return task
