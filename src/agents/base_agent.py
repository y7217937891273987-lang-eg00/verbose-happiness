"""Base Agent - Foundation for all specialized agents"""

from typing import Any, Dict, Optional
from src.core.agent_framework import Agent, AgentType, AgentTask
import logging

logger = logging.getLogger(__name__)


class BaseAgent(Agent):
    """Extended base agent with common functionality"""

    def __init__(
        self,
        agent_id: str,
        agent_type: AgentType,
        name: str,
        capabilities: list,
        llm_manager=None,
        system_prompt: Optional[str] = None
    ):
        super().__init__(agent_id, agent_type, name, capabilities, llm_manager)
        self.system_prompt = system_prompt or self._default_system_prompt()

    def _default_system_prompt(self) -> str:
        """Default system prompt for this agent"""
        return f"You are {self.name}, an AI agent specialized in: {', '.join(self.capabilities)}"

    async def think(self, prompt: str) -> str:
        """Use LLM to think about a problem"""
        if not self.llm_manager:
            logger.warning(f"{self.name} has no LLM manager configured")
            return "No LLM available"
        
        response = await self.llm_manager.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
            temperature=0.7,
            max_tokens=2000
        )
        return response

    async def analyze(self, content: str, analysis_type: str = "general") -> Dict[str, Any]:
        """Analyze content and return structured results"""
        prompt = f"Analyze the following {analysis_type}:\n\n{content}\n\nProvide key findings and insights."
        analysis = await self.think(prompt)
        return {
            "type": analysis_type,
            "content": content[:500],  # Summary
            "analysis": analysis,
            "agent": self.name
        }
