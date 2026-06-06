"""Task Decomposer - Breaks down complex tasks into sub-tasks"""

from typing import List, Dict, Any
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TaskNode:
    """Represents a task node in decomposition tree"""
    task_id: str
    description: str
    task_type: str  # 'research', 'code', 'business', 'analysis'
    priority: int
    parent_id: str = None
    dependencies: List[str] = None
    estimated_duration: int = None  # seconds


class TaskDecomposer:
    """Decomposes complex tasks into manageable sub-tasks"""

    def __init__(self, llm_manager=None):
        self.llm_manager = llm_manager
        self.decomposition_history = []

    async def decompose(
        self,
        main_task: str,
        max_depth: int = 3,
        use_llm: bool = True
    ) -> List[TaskNode]:
        """
        Decompose a main task into sub-tasks.
        
        Args:
            main_task: The main task description
            max_depth: Maximum decomposition depth
            use_llm: Whether to use LLM for intelligent decomposition
        
        Returns:
            List of TaskNode objects representing the decomposition tree
        """
        logger.info(f"Decomposing task: {main_task}")
        
        tasks = []
        
        if use_llm and self.llm_manager:
            # Use LLM to intelligently decompose
            tasks = await self._decompose_with_llm(main_task, max_depth)
        else:
            # Use rule-based decomposition
            tasks = self._decompose_with_rules(main_task)
        
        self.decomposition_history.append({
            "main_task": main_task,
            "sub_tasks": len(tasks),
            "tasks": [t.description for t in tasks]
        })
        
        return tasks

    async def _decompose_with_llm(self, main_task: str, max_depth: int) -> List[TaskNode]:
        """
        Use LLM to intelligently break down task.
        This will be fully implemented in Phase 2.
        """
        logger.info(f"Using LLM for task decomposition (depth: {max_depth})")
        
        # Placeholder for LLM integration
        prompt = f"""
        Break down this task into 3-5 specific sub-tasks:
        
        Main Task: {main_task}
        
        Return JSON with format:
        {{
            "sub_tasks": [
                {{
                    "description": "...",
                    "type": "research|code|business|analysis",
                    "priority": 1-10,
                    "dependencies": ["task_id_1", "task_id_2"]
                }}
            ]
        }}
        """
        
        # TODO: Implement LLM call via self.llm_manager
        # For now, return basic decomposition
        return self._decompose_with_rules(main_task)

    def _decompose_with_rules(self, main_task: str) -> List[TaskNode]:
        """
        Rule-based task decomposition.
        Identifies task type and breaks it into logical sub-tasks.
        """
        task_lower = main_task.lower()
        tasks = []
        
        # Identify task type
        if any(word in task_lower for word in ['research', 'find', 'analyze', 'investigate']):
            tasks = self._decompose_research_task(main_task)
        elif any(word in task_lower for word in ['code', 'build', 'create', 'develop', 'write']):
            tasks = self._decompose_code_task(main_task)
        elif any(word in task_lower for word in ['business', 'store', 'shop', 'sell', 'automate']):
            tasks = self._decompose_business_task(main_task)
        else:
            tasks = self._decompose_generic_task(main_task)
        
        return tasks

    def _decompose_research_task(self, task: str) -> List[TaskNode]:
        """Decompose research tasks"""
        import uuid
        base_id = str(uuid.uuid4())[:8]
        
        return [
            TaskNode(
                task_id=f"{base_id}-1",
                description=f"Search for information on: {task}",
                task_type="research",
                priority=9,
                estimated_duration=300
            ),
            TaskNode(
                task_id=f"{base_id}-2",
                description="Analyze and summarize findings",
                task_type="analysis",
                priority=8,
                parent_id=f"{base_id}-1",
                dependencies=[f"{base_id}-1"],
                estimated_duration=180
            )
        ]

    def _decompose_code_task(self, task: str) -> List[TaskNode]:
        """Decompose code development tasks"""
        import uuid
        base_id = str(uuid.uuid4())[:8]
        
        return [
            TaskNode(
                task_id=f"{base_id}-1",
                description="Research requirements and best practices",
                task_type="research",
                priority=8,
                estimated_duration=300
            ),
            TaskNode(
                task_id=f"{base_id}-2",
                description="Generate code implementation",
                task_type="code",
                priority=9,
                parent_id=f"{base_id}-1",
                dependencies=[f"{base_id}-1"],
                estimated_duration=600
            ),
            TaskNode(
                task_id=f"{base_id}-3",
                description="Test and validate code",
                task_type="analysis",
                priority=9,
                parent_id=f"{base_id}-2",
                dependencies=[f"{base_id}-2"],
                estimated_duration=300
            )
        ]

    def _decompose_business_task(self, task: str) -> List[TaskNode]:
        """Decompose business automation tasks"""
        import uuid
        base_id = str(uuid.uuid4())[:8]
        
        return [
            TaskNode(
                task_id=f"{base_id}-1",
                description="Analyze business requirements",
                task_type="analysis",
                priority=9,
                estimated_duration=300
            ),
            TaskNode(
                task_id=f"{base_id}-2",
                description="Set up business infrastructure",
                task_type="business",
                priority=9,
                parent_id=f"{base_id}-1",
                dependencies=[f"{base_id}-1"],
                estimated_duration=600
            ),
            TaskNode(
                task_id=f"{base_id}-3",
                description="Configure automation and management",
                task_type="business",
                priority=8,
                parent_id=f"{base_id}-2",
                dependencies=[f"{base_id}-2"],
                estimated_duration=400
            )
        ]

    def _decompose_generic_task(self, task: str) -> List[TaskNode]:
        """Decompose generic tasks"""
        import uuid
        base_id = str(uuid.uuid4())[:8]
        
        return [
            TaskNode(
                task_id=f"{base_id}-1",
                description=f"Process task: {task}",
                task_type="analysis",
                priority=5,
                estimated_duration=300
            )
        ]
