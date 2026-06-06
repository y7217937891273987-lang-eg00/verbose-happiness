"""Agent Framework - Core orchestration system for multi-agent task execution"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    WORKING = "working"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentType(Enum):
    """Types of agents"""
    RESEARCH = "research"
    CODE = "code"
    BUSINESS = "business"
    ORCHESTRATOR = "orchestrator"
    GENERIC = "generic"


@dataclass
class AgentTask:
    """Represents a task assigned to an agent"""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    parent_task_id: Optional[str] = None
    priority: int = 5  # 1-10, higher = more important
    status: AgentStatus = AgentStatus.IDLE
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    requires_approval: bool = False
    approval_status: Optional[bool] = None


@dataclass
class ExecutionPlan:
    """Execution plan for a main task"""
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    main_task: AgentTask = field(default_factory=AgentTask)
    sub_tasks: List[AgentTask] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)  # task_id -> [dependent_task_ids]
    created_at: datetime = field(default_factory=datetime.now)


class Agent:
    """Base Agent class - all agents inherit from this"""

    def __init__(
        self,
        agent_id: str,
        agent_type: AgentType,
        name: str,
        capabilities: List[str],
        llm_manager=None
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.name = name
        self.capabilities = capabilities
        self.llm_manager = llm_manager
        self.status = AgentStatus.IDLE
        self.current_task: Optional[AgentTask] = None
        self.task_history: List[AgentTask] = []

    async def execute(self, task: AgentTask) -> Any:
        """
        Execute a task. Override in subclasses.
        Returns result or None if needs approval
        """
        self.current_task = task
        self.status = AgentStatus.WORKING
        task.started_at = datetime.now()
        
        try:
            logger.info(f"Agent {self.name} executing task {task.task_id}: {task.description}")
            result = await self._execute_internal(task)
            
            task.status = AgentStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.now()
            self.status = AgentStatus.IDLE
            self.task_history.append(task)
            
            return result
        except Exception as e:
            logger.error(f"Agent {self.name} failed on task {task.task_id}: {str(e)}")
            task.status = AgentStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            self.status = AgentStatus.IDLE
            self.task_history.append(task)
            raise

    async def _execute_internal(self, task: AgentTask) -> Any:
        """Override in subclasses"""
        return {"message": f"Task processed by {self.name}", "task_id": task.task_id}

    def can_handle(self, task: AgentTask) -> bool:
        """Check if agent can handle this task"""
        # Check if task keywords match agent capabilities
        task_keywords = set(task.description.lower().split())
        agent_keywords = set(" ".join(self.capabilities).lower().split())
        return len(task_keywords & agent_keywords) > 0 or not self.capabilities

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "type": self.agent_type.value,
            "status": self.status.value,
            "current_task": self.current_task.task_id if self.current_task else None,
            "tasks_completed": len(self.task_history)
        }


class AgentFramework:
    """Main orchestration framework for managing multiple agents"""

    def __init__(self, llm_manager=None):
        self.agents: Dict[str, Agent] = {}
        self.execution_plans: Dict[str, ExecutionPlan] = {}
        self.llm_manager = llm_manager
        self.approval_callback: Optional[Callable] = None
        logger.info("AgentFramework initialized")

    def register_agent(self, agent: Agent) -> None:
        """Register an agent"""
        self.agents[agent.agent_id] = agent
        logger.info(f"Agent registered: {agent.name} ({agent.agent_id})")

    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Agent unregistered: {agent_id}")

    def set_approval_callback(self, callback: Callable) -> None:
        """Set callback for approval requests"""
        self.approval_callback = callback

    async def decompose_and_execute(
        self,
        main_task_description: str,
        require_approval: bool = True
    ) -> ExecutionPlan:
        """
        Main entry point: Takes a task description, decomposes it,
        creates execution plan, and executes with available agents.
        """
        logger.info(f"Decomposing main task: {main_task_description}")
        
        # Create main task
        main_task = AgentTask(
            description=main_task_description,
            priority=10,
            requires_approval=require_approval
        )
        
        # Create execution plan
        plan = ExecutionPlan(main_task=main_task)
        self.execution_plans[plan.plan_id] = plan
        
        # TODO: Integrate TaskDecomposer here
        # For now, treat as single task
        plan.sub_tasks = [main_task]
        
        # Execute with best matching agent
        await self._execute_plan(plan)
        
        return plan

    async def _execute_plan(self, plan: ExecutionPlan) -> None:
        """Execute all tasks in a plan"""
        for task in plan.sub_tasks:
            # Find best matching agent
            best_agent = self._find_best_agent(task)
            
            if not best_agent:
                logger.warning(f"No agent found for task: {task.description}")
                task.status = AgentStatus.FAILED
                task.error = "No suitable agent available"
                continue
            
            # Check if approval needed
            if task.requires_approval and self.approval_callback:
                logger.info(f"Requesting approval for task {task.task_id}")
                task.status = AgentStatus.WAITING_APPROVAL
                approved = await self.approval_callback(task)
                task.approval_status = approved
                
                if not approved:
                    logger.info(f"Task {task.task_id} rejected by user")
                    task.status = AgentStatus.FAILED
                    task.error = "Rejected by user"
                    continue
            
            # Execute task
            try:
                await best_agent.execute(task)
            except Exception as e:
                logger.error(f"Task execution failed: {str(e)}")

    def _find_best_agent(self, task: AgentTask) -> Optional[Agent]:
        """Find the best agent to handle a task"""
        candidates = [agent for agent in self.agents.values() if agent.can_handle(task)]
        
        if not candidates:
            return None
        
        # Sort by availability and capability match
        return sorted(
            candidates,
            key=lambda a: (a.status == AgentStatus.IDLE, len(a.task_history)),
            reverse=True
        )[0]

    def get_framework_status(self) -> Dict[str, Any]:
        """Get overall framework status"""
        return {
            "agents": {agent_id: agent.get_status() for agent_id, agent in self.agents.items()},
            "total_agents": len(self.agents),
            "active_plans": len([p for p in self.execution_plans.values()]),
            "execution_plans": {
                plan_id: {
                    "main_task_id": plan.main_task.task_id,
                    "sub_tasks_count": len(plan.sub_tasks),
                    "created_at": plan.created_at.isoformat()
                }
                for plan_id, plan in self.execution_plans.items()
            }
        }

    async def execute_with_agents(self, task_description: str) -> Dict[str, Any]:
        """High-level execution method"""
        plan = await self.decompose_and_execute(task_description)
        return {
            "plan_id": plan.plan_id,
            "status": "completed",
            "results": [task.result for task in plan.sub_tasks if task.status == AgentStatus.COMPLETED]
        }
