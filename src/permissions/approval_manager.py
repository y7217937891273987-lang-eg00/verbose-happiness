"""Approval Manager - Handles permission and approval workflows"""

import logging
from datetime import datetime
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    """Approval workflow status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class ApprovalRequest:
    """Represents an approval request"""
    request_id: str
    description: str
    required_action: str  # 'code_modification', 'internet_access', 'business_setup'
    details: Dict[str, Any]
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = None
    expires_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    reason: Optional[str] = None  # User's reason for approval/rejection

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class ApprovalManager:
    """
    Manages approval workflows.
    
    Features:
    - Request/approve/reject actions that require permission
    - Transparency: shows what needs to be added/changed
    - User callback for UI approval dialogs
    - Time-delayed approvals
    - Audit trail
    """

    def __init__(self, approval_timeout_seconds: int = 3600):
        self.approval_timeout = approval_timeout_seconds
        self.pending_requests: Dict[str, ApprovalRequest] = {}
        self.approved_requests: Dict[str, ApprovalRequest] = {}
        self.rejected_requests: Dict[str, ApprovalRequest] = {}
        self.approval_callback: Optional[Callable] = None
        logger.info("ApprovalManager initialized")

    def set_approval_callback(self, callback: Callable) -> None:
        """
        Set callback function for approval UI.
        Callback signature: async def callback(request: ApprovalRequest) -> bool
        """
        self.approval_callback = callback
        logger.info("Approval callback registered")

    async def request_approval(
        self,
        request_id: str,
        description: str,
        required_action: str,
        details: Dict[str, Any],
        auto_approve: bool = False
    ) -> bool:
        """
        Request user approval for an action.
        
        Returns:
            True if approved, False if rejected
        """
        logger.info(f"Approval requested: {request_id} - {description}")
        
        request = ApprovalRequest(
            request_id=request_id,
            description=description,
            required_action=required_action,
            details=details
        )
        
        self.pending_requests[request_id] = request
        
        # If callback registered, use it
        if self.approval_callback and not auto_approve:
            approved = await self.approval_callback(request)
            return await self.respond_to_approval(request_id, approved)
        
        # Auto-approve for testing
        if auto_approve:
            return await self.respond_to_approval(request_id, True)
        
        logger.warning(f"No approval callback registered for {request_id}")
        return False

    async def respond_to_approval(
        self,
        request_id: str,
        approved: bool,
        reason: str = ""
    ) -> bool:
        """
        User responds to approval request.
        """
        if request_id not in self.pending_requests:
            logger.warning(f"Approval request not found: {request_id}")
            return False
        
        request = self.pending_requests.pop(request_id)
        request.approved_at = datetime.now()
        request.reason = reason
        
        if approved:
            request.status = ApprovalStatus.APPROVED
            self.approved_requests[request_id] = request
            logger.info(f"Approval granted for {request_id}")
        else:
            request.status = ApprovalStatus.REJECTED
            self.rejected_requests[request_id] = request
            logger.info(f"Approval rejected for {request_id}")
        
        return approved

    def get_pending_requests(self) -> Dict[str, ApprovalRequest]:
        """Get all pending approval requests"""
        return self.pending_requests.copy()

    def get_request_history(self, limit: int = 50) -> Dict[str, Any]:
        """Get approval request history"""
        approved = list(self.approved_requests.values())[-limit:]
        rejected = list(self.rejected_requests.values())[-limit:]
        
        return {
            "approved": [self._serialize_request(r) for r in approved],
            "rejected": [self._serialize_request(r) for r in rejected]
        }

    def _serialize_request(self, request: ApprovalRequest) -> Dict[str, Any]:
        """Convert approval request to dict"""
        return {
            "request_id": request.request_id,
            "description": request.description,
            "action": request.required_action,
            "status": request.status.value,
            "created_at": request.created_at.isoformat(),
            "reason": request.reason
        }
