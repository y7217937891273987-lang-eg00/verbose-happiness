"""Knowledge Learner - Learn from task results and build knowledge base"""

import logging
import json
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class KnowledgeLearner:
    """
    Learns from task execution results.
    Builds a knowledge base of:
    - Successful task patterns
    - Common issues and solutions
    - Agent performance metrics
    """

    def __init__(self, knowledge_db_path: str = "models/knowledge_base.json"):
        self.db_path = Path(knowledge_db_path)
        self.knowledge_base = self._load_knowledge_base()
        logger.info("KnowledgeLearner initialized")

    def _load_knowledge_base(self) -> Dict[str, Any]:
        """
        Load knowledge base from disk.
        """
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading knowledge base: {str(e)}")
        
        return {
            "task_patterns": {},
            "solutions": {},
            "agent_performance": {},
            "learned_skills": [],
            "common_issues": {}
        }

    def _save_knowledge_base(self) -> None:
        """
        Save knowledge base to disk.
        """
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.db_path, 'w') as f:
                json.dump(self.knowledge_base, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving knowledge base: {str(e)}")

    async def learn_from_task(
        self,
        task_description: str,
        result: Any,
        agent_name: str,
        execution_time: float,
        success: bool
    ) -> None:
        """
        Extract and store learning from a completed task.
        """
        logger.info(f"Learning from task: {task_description[:50]}...")
        
        # Extract task pattern
        pattern_key = self._extract_pattern(task_description)
        
        if pattern_key not in self.knowledge_base["task_patterns"]:
            self.knowledge_base["task_patterns"][pattern_key] = {
                "examples": [],
                "success_rate": 0,
                "avg_time": 0
            }
        
        # Store execution data
        pattern_data = self.knowledge_base["task_patterns"][pattern_key]
        pattern_data["examples"].append({
            "task": task_description,
            "result": str(result)[:500],
            "agent": agent_name,
            "success": success,
            "time": execution_time,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update agent performance
        if agent_name not in self.knowledge_base["agent_performance"]:
            self.knowledge_base["agent_performance"][agent_name] = {
                "tasks_completed": 0,
                "success_count": 0,
                "avg_execution_time": 0
            }
        
        agent_perf = self.knowledge_base["agent_performance"][agent_name]
        agent_perf["tasks_completed"] += 1
        if success:
            agent_perf["success_count"] += 1
        
        # Update success rate
        pattern_data["success_rate"] = (
            len([e for e in pattern_data["examples"] if e["success"]]) / len(pattern_data["examples"])
        )
        
        self._save_knowledge_base()

    def _extract_pattern(self, task_description: str) -> str:
        """
        Extract task pattern from description.
        Uses keywords to categorize tasks.
        """
        keywords = {
            "research": ["research", "find", "investigate", "analyze"],
            "code": ["code", "build", "create", "develop", "write", "generate"],
            "business": ["business", "automation", "setup", "create", "store", "shop"],
            "analysis": ["analyze", "evaluate", "assess", "review"]
        }
        
        task_lower = task_description.lower()
        for pattern, keywords_list in keywords.items():
            if any(kw in task_lower for kw in keywords_list):
                return pattern
        
        return "general"

    def get_agent_performance(self, agent_name: str = None) -> Dict[str, Any]:
        """
        Get performance metrics for an agent.
        """
        if agent_name:
            return self.knowledge_base["agent_performance"].get(agent_name, {})
        return self.knowledge_base["agent_performance"]

    def get_task_patterns(self) -> Dict[str, Any]:
        """
        Get learned task patterns.
        """
        return self.knowledge_base["task_patterns"]

    def get_solution_for_pattern(self, pattern: str) -> List[Dict[str, Any]]:
        """
        Get known solutions for a task pattern.
        """
        if pattern in self.knowledge_base["task_patterns"]:
            return self.knowledge_base["task_patterns"][pattern]["examples"]
        return []

    def suggest_improvement_opportunities(self) -> List[Dict[str, Any]]:
        """
        Suggest where the system could improve based on learned patterns.
        """
        opportunities = []
        
        # Find patterns with low success rate
        for pattern, data in self.knowledge_base["task_patterns"].items():
            if data["success_rate"] < 0.7 and len(data["examples"]) > 3:
                opportunities.append({
                    "type": "low_success_rate",
                    "pattern": pattern,
                    "success_rate": data["success_rate"],
                    "suggestion": f"Improve handling of {pattern} tasks (currently {data['success_rate']*100:.1f}% success)"
                })
        
        # Find slow patterns
        for pattern, data in self.knowledge_base["task_patterns"].items():
            avg_time = sum(e["time"] for e in data["examples"]) / len(data["examples"])
            if avg_time > 60:  # More than 60 seconds
                opportunities.append({
                    "type": "slow_execution",
                    "pattern": pattern,
                    "avg_time": avg_time,
                    "suggestion": f"Optimize {pattern} tasks (currently {avg_time:.1f}s average)"
                })
        
        return opportunities
