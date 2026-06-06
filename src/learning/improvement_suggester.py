"""Improvement Suggester - Suggest enhancements to agent capabilities"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Improvement:
    """Represents a suggested improvement"""
    improvement_id: str
    agent_name: str
    capability: str
    current_score: float  # 0-1
    proposed_enhancement: str
    estimated_impact: float  # 0-1
    implementation_effort: str  # 'low', 'medium', 'high'
    reasoning: str


class ImprovementSuggester:
    """
    Analyzes agent performance and suggests improvements.
    
    Suggests enhancements to:
    - Agent capabilities
    - Task decomposition strategies
    - Code quality
    - Response accuracy
    """

    def __init__(self, knowledge_learner=None, code_modifier=None):
        self.knowledge_learner = knowledge_learner
        self.code_modifier = code_modifier
        self.suggestions = []
        logger.info("ImprovementSuggester initialized")

    async def analyze_and_suggest(
        self,
        agent_name: str,
        performance_metrics: Dict[str, Any]
    ) -> List[Improvement]:
        """
        Analyze agent performance and suggest improvements.
        """
        logger.info(f"Analyzing {agent_name} for improvement opportunities")
        
        suggestions = []
        
        # Analyze success rate
        success_rate = performance_metrics.get("success_rate", 0)
        if success_rate < 0.8:
            suggestion = Improvement(
                improvement_id=f"improve-{agent_name}-success",
                agent_name=agent_name,
                capability="task_completion",
                current_score=success_rate,
                proposed_enhancement="Enhance error handling and task recovery",
                estimated_impact=0.15,
                implementation_effort="medium",
                reasoning=f"Agent success rate is {success_rate*100:.1f}%. Improving error handling could increase this."
            )
            suggestions.append(suggestion)
        
        # Analyze execution time
        avg_time = performance_metrics.get("avg_execution_time", 0)
        if avg_time > 30:  # More than 30 seconds
            suggestion = Improvement(
                improvement_id=f"improve-{agent_name}-speed",
                agent_name=agent_name,
                capability="execution_speed",
                current_score=1 - min(avg_time / 60, 1),  # 0-1 based on time
                proposed_enhancement="Optimize prompt engineering and API calls",
                estimated_impact=0.20,
                implementation_effort="low",
                reasoning=f"Average execution time is {avg_time:.1f}s. Better prompts could improve speed."
            )
            suggestions.append(suggestion)
        
        self.suggestions.extend(suggestions)
        return suggestions

    async def suggest_skill_addition(
        self,
        agent_name: str,
        current_skills: List[str],
        unmet_task_types: List[str]
    ) -> List[Improvement]:
        """
        Suggest new skills for an agent based on unmet task types.
        """
        logger.info(f"Suggesting skills for {agent_name}")
        
        suggestions = []
        
        for task_type in unmet_task_types:
            if task_type not in current_skills:
                suggestion = Improvement(
                    improvement_id=f"skill-{agent_name}-{task_type}",
                    agent_name=agent_name,
                    capability=f"handle_{task_type}",
                    current_score=0,
                    proposed_enhancement=f"Add capability to handle {task_type} tasks",
                    estimated_impact=0.25,
                    implementation_effort="medium",
                    reasoning=f"Recent tasks show need for {task_type} capability. This could improve versatility."
                )
                suggestions.append(suggestion)
        
        return suggestions

    async def suggest_code_improvements(
        self,
        agent_code_path: str
    ) -> List[Improvement]:
        """
        Analyze agent code and suggest improvements.
        Uses CodeModifier for detailed analysis.
        """
        if not self.code_modifier:
            logger.warning("CodeModifier not available")
            return []
        
        try:
            with open(agent_code_path, 'r') as f:
                code = f.read()
            
            analysis = await self.code_modifier.analyze_code(code, "general")
            
            suggestions = []
            for issue in analysis.get("issues", []):
                suggestion = Improvement(
                    improvement_id=f"code-{issue['type']}",
                    agent_name="code_quality",
                    capability=issue['type'],
                    current_score=0.5,
                    proposed_enhancement=f"Fix {issue['message']}",
                    estimated_impact=0.1,
                    implementation_effort="low",
                    reasoning=f"Code analysis found: {issue['message']}"
                )
                suggestions.append(suggestion)
            
            return suggestions
        
        except Exception as e:
            logger.error(f"Error analyzing code: {str(e)}")
            return []

    def get_highest_priority_improvements(self, limit: int = 5) -> List[Improvement]:
        """
        Get highest priority improvements to implement.
        Sorted by estimated_impact * (1 - implementation_effort_score)
        """
        effort_scores = {"low": 0.2, "medium": 0.5, "high": 0.8}
        
        scored = [
            (s, s.estimated_impact * (1 - effort_scores.get(s.implementation_effort, 0.5)))
            for s in self.suggestions
        ]
        
        return [s for s, _ in sorted(scored, key=lambda x: x[1], reverse=True)][:limit]

    def get_suggestions_by_agent(self, agent_name: str) -> List[Improvement]:
        """Get all suggestions for a specific agent"""
        return [s for s in self.suggestions if s.agent_name == agent_name]
