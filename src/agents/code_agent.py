"""Code Agent - Generates, analyzes, and modifies code"""

from typing import Dict, Any, Optional
from src.agents.base_agent import BaseAgent
from src.core.agent_framework import AgentType, AgentTask
import logging

logger = logging.getLogger(__name__)


class CodeAgent(BaseAgent):
    """Agent specialized in code generation and analysis"""

    def __init__(self, llm_manager=None):
        super().__init__(
            agent_id="code-001",
            agent_type=AgentType.CODE,
            name="Code Agent",
            capabilities=["code", "programming", "development", "debug", "build", "write"],
            llm_manager=llm_manager,
            system_prompt="You are an expert programmer. Write clean, efficient, well-documented code. Always include error handling."
        )

    async def _execute_internal(self, task: AgentTask) -> Any:
        """Execute code task"""
        logger.info(f"Code Agent processing: {task.description}")
        
        code = await self.generate_code(task.description)
        return {
            "task": task.description,
            "code": code,
            "status": "generated"
        }

    async def generate_code(
        self,
        requirement: str,
        language: str = "python",
        with_tests: bool = True
    ) -> str:
        """
        Generate code from a requirement description.
        Phase 2: Add approval workflow for code modifications.
        """
        logger.info(f"Generating {language} code for: {requirement}")
        
        prompt = f"""
        Write production-quality {language} code that: {requirement}
        
        Requirements:
        - Use best practices
        - Include error handling
        - Add type hints (Python)
        - Include docstrings
        {f"- Include unit tests" if with_tests else ""}
        """
        
        code = await self.think(prompt)
        return code

    async def analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze code for issues, improvements"""
        logger.info("Analyzing code")
        
        analysis = await self.think(
            f"Analyze this code and provide:\n1. Potential issues\n2. Performance improvements\n3. Security concerns\n\n{code}"
        )
        
        return {
            "code_length": len(code),
            "analysis": analysis
        }

    async def fix_code(self, code: str, issue: str) -> str:
        """
        Fix code based on described issue.
        Phase 2: Will require approval before applying changes.
        """
        logger.info(f"Fixing code issue: {issue}")
        
        fixed = await self.think(
            f"Fix the following issue in this code:\n\nIssue: {issue}\n\nCode:\n{code}"
        )
        
        return fixed
