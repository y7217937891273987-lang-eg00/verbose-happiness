"""Audit Log - Transparency and tracking of all agent actions"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)


class AuditLog:
    """
    Logs all significant actions for transparency and debugging.
    
    Logs:
    - Agent actions and decisions
    - Approval requests and responses
    - Code modifications
    - Internet access requests
    - Business automation steps
    """

    def __init__(self, log_file: str = "logs/audit.log"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.in_memory_log: List[Dict[str, Any]] = []
        logger.info(f"AuditLog initialized: {log_file}")

    def log_action(
        self,
        action_type: str,
        actor: str,
        description: str,
        details: Dict[str, Any] = None,
        status: str = "completed"
    ) -> None:
        """
        Log an action.
        
        Args:
            action_type: Type of action ('agent_task', 'approval', 'code_change', 'internet_access')
            actor: Who performed the action (agent name, user, system)
            description: Human-readable description
            details: Additional context
            status: 'completed', 'pending', 'failed'
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "actor": actor,
            "description": description,
            "status": status,
            "details": details or {}
        }
        
        self.in_memory_log.append(log_entry)
        self._write_to_file(log_entry)
        logger.debug(f"Logged {action_type}: {description}")

    def _write_to_file(self, entry: Dict[str, Any]) -> None:
        """Write audit log entry to file"""
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error(f"Error writing audit log: {str(e)}")

    def log_agent_task(
        self,
        agent_name: str,
        task_id: str,
        description: str,
        result: Any = None,
        error: str = None
    ) -> None:
        """Log agent task execution"""
        self.log_action(
            action_type="agent_task",
            actor=agent_name,
            description=f"Task {task_id}: {description}",
            details={
                "task_id": task_id,
                "result": str(result)[:500] if result else None,
                "error": error
            },
            status="completed" if error is None else "failed"
        )

    def log_approval_request(
        self,
        request_id: str,
        action: str,
        approved: bool,
        details: Dict[str, Any] = None
    ) -> None:
        """Log approval decision"""
        self.log_action(
            action_type="approval",
            actor="user",
            description=f"Approval for {action}",
            details={
                "request_id": request_id,
                "action": action,
                "approved": approved,
                **details
            }
        )

    def log_code_modification(
        self,
        file_path: str,
        modification_type: str,  # 'create', 'update', 'delete'
        changes: str,
        approved: bool = None
    ) -> None:
        """Log code modifications"""
        self.log_action(
            action_type="code_change",
            actor="code_agent",
            description=f"{modification_type.title()} file: {file_path}",
            details={
                "file_path": file_path,
                "type": modification_type,
                "changes_summary": changes[:500],
                "approved": approved
            }
        )

    def log_internet_access(
        self,
        purpose: str,
        url_or_query: str,
        approved: bool = None,
        result: str = None
    ) -> None:
        """Log internet access requests"""
        self.log_action(
            action_type="internet_access",
            actor="research_agent",
            description=f"Internet access for: {purpose}",
            details={
                "purpose": purpose,
                "url_or_query": url_or_query,
                "approved": approved,
                "result": result[:500] if result else None
            }
        )

    def get_log_summary(self, action_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get log entries (optionally filtered by type)"""
        logs = self.in_memory_log
        
        if action_type:
            logs = [log for log in logs if log["action_type"] == action_type]
        
        return logs[-limit:]
