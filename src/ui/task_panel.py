"""Task Panel - Task input and submission UI"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class TaskPanel:
    """
    Panel for task input and submission.
    Features:
    - Task description input
    - Task type selection
    - Approval requirement toggle
    - Submission button
    """

    def __init__(self):
        self.last_task = None
        logger.info("TaskPanel initialized")

    def get_task_info(self, values: Dict) -> Dict[str, Any]:
        """
        Extract task information from form values.
        """
        return {
            "description": values.get("-TASK_INPUT-", ""),
            "task_type": values.get("-TASK_TYPE-", "Auto-detect"),
            "require_approval": values.get("-REQUIRE_APPROVAL-", True)
        }

    def validate_task(self, task_description: str) -> tuple:
        """
        Validate task input.
        Returns: (is_valid, error_message)
        """
        if not task_description or len(task_description.strip()) < 10:
            return False, "Task description must be at least 10 characters"
        if len(task_description) > 10000:
            return False, "Task description cannot exceed 10000 characters"
        return True, ""
