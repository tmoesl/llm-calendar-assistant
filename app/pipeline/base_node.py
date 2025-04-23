"""
Base node class for pipeline processing.
All pipeline nodes inherit from this base class.
"""

from app.models.schemas import TaskEvent


class BaseNode:
    """Base class for all pipeline nodes"""

    def process(self, task: TaskEvent) -> TaskEvent:
        """
        Process the task and update its state

        Args:
            task: TaskEvent containing user input and current state

        Returns:
            Updated TaskEvent with new state and metadata
        """
        raise NotImplementedError
