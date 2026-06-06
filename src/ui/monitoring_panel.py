"""Monitoring Panel - Real-time task execution monitoring"""

import logging
from typing import Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TaskStatus:
    """Task status information"""
    task_id: str
    description: str
    agent: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    progress: int  # 0-100
    message: str


class MonitoringPanel:
    """
    Real-time monitoring of task execution.
    Shows:
    - Currently executing tasks
    - Progress of each task
    - Agent status
    - System health
    """

    def __init__(self):
        self.active_tasks: Dict[str, TaskStatus] = {}
        logger.info("MonitoringPanel initialized")

    def update_task_status(
        self,
        task_id: str,
        status: str,
        progress: int = 0,
        message: str = ""
    ) -> None:
        """
        Update task status for display.
        """
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = status
            task.progress = progress
            task.message = message
            logger.debug(f"Updated task {task_id}: {status} ({progress}%)")

    def get_status_summary(self) -> Dict[str, Any]:
        """
        Get summary of all active tasks.
        """
        return {
            "total_tasks": len(self.active_tasks),
            "running": len([t for t in self.active_tasks.values() if t.status == "running"]),
            "completed": len([t for t in self.active_tasks.values() if t.status == "completed"]),
            "failed": len([t for t in self.active_tasks.values() if t.status == "failed"]),
            "tasks": [{"id": t.task_id, "agent": t.agent, "status": t.status, "progress": t.progress} 
                      for t in self.active_tasks.values()]
        }
