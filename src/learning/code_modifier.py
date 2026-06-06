"""Code Modifier - Agent-driven code improvements"""

import logging
import ast
import asyncio
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class CodeModification:
    """Represents a proposed code modification"""
    file_path: str
    modification_type: str  # 'improvement', 'bugfix', 'optimization', 'refactor'
    description: str  # What's being changed and why
    original_code: str
    modified_code: str
    reasoning: str  # Why this change improves the code
    impact_analysis: Dict[str, Any]  # Potential side effects


class CodeModifier:
    """
    Analyzes code and suggests improvements.
    When approved by user, applies modifications.
    
    Capabilities:
    - Analyze code for issues
    - Suggest optimizations
    - Apply changes with approval
    - Rollback if needed
    """

    def __init__(self, llm_manager=None):
        self.llm_manager = llm_manager
        self.modification_history = []
        self.rollback_stack = []
        logger.info("CodeModifier initialized")

    async def analyze_code(
        self,
        code: str,
        analysis_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Analyze code for issues and improvement opportunities.
        
        Args:
            code: Python code to analyze
            analysis_type: Type of analysis ('general', 'performance', 'security', 'style')
        
        Returns:
            Analysis results with findings
        """
        logger.info(f"Analyzing code ({analysis_type})")
        
        analysis = {
            "type": analysis_type,
            "issues": [],
            "improvements": [],
            "quality_score": 0
        }
        
        # Static analysis
        analysis["issues"].extend(self._static_analysis(code))
        
        # Use LLM for deeper analysis
        if self.llm_manager:
            analysis["improvements"] = await self._llm_analysis(code, analysis_type)
        
        # Calculate quality score
        analysis["quality_score"] = 100 - (len(analysis["issues"]) * 10)
        
        return analysis

    def _static_analysis(self, code: str) -> list:
        """
        Static code analysis using AST.
        """
        issues = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # Check for bare except
                if isinstance(node, ast.ExceptHandler):
                    if node.type is None:
                        issues.append({
                            "type": "bare_except",
                            "line": node.lineno,
                            "message": "Bare 'except:' clause - should catch specific exceptions"
                        })
                
                # Check for unused variables
                if isinstance(node, ast.FunctionDef):
                    args = {arg.arg for arg in node.args.args}
                    used = set()
                    for n in ast.walk(node):
                        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                            used.add(n.id)
                    unused = args - used
                    for var in unused:
                        issues.append({
                            "type": "unused_variable",
                            "variable": var,
                            "message": f"Unused parameter: {var}"
                        })
        
        except SyntaxError as e:
            issues.append({
                "type": "syntax_error",
                "line": e.lineno,
                "message": str(e)
            })
        
        return issues

    async def _llm_analysis(
        self,
        code: str,
        analysis_type: str
    ) -> list:
        """
        Use LLM for deep code analysis.
        """
        prompt = f"""
        Analyze this {analysis_type} {analysis_type} and suggest improvements:
        
        {code}
        
        Provide:
        1. Issues found
        2. Suggested improvements
        3. Priority (high/medium/low)
        4. Reasoning for each change
        """
        
        analysis_text = await self.llm_manager.generate(
            prompt=prompt,
            system_prompt="You are a Python code review expert.",
            temperature=0.5,
            max_tokens=1500
        )
        
        return [{"llm_analysis": analysis_text}]

    async def suggest_modifications(
        self,
        code: str,
        analysis: Dict[str, Any]
    ) -> list:
        """
        Suggest specific code modifications based on analysis.
        
        Returns:
            List of CodeModification objects
        """
        logger.info("Suggesting modifications based on analysis")
        
        modifications = []
        
        if not self.llm_manager:
            logger.warning("LLM manager not available for suggestions")
            return modifications
        
        # For each improvement, generate modification
        for improvement in analysis.get("improvements", []):
            prompt = f"""
            Generate improved version of this code:
            
            {code}
            
            Improvement needed: {improvement}
            
            Return ONLY the modified code, no explanations.
            """
            
            modified_code = await self.llm_manager.generate(
                prompt=prompt,
                system_prompt="You are a Python code expert. Return only valid Python code.",
                temperature=0.5,
                max_tokens=2000
            )
            
            modification = CodeModification(
                file_path="unknown",
                modification_type="improvement",
                description=str(improvement),
                original_code=code,
                modified_code=modified_code,
                reasoning="LLM-suggested improvement",
                impact_analysis={"complexity": "medium", "test_coverage": "recommended"}
            )
            
            modifications.append(modification)
        
        return modifications

    async def apply_modification(
        self,
        modification: CodeModification,
        file_path: str,
        approval_manager=None
    ) -> Tuple[bool, str]:
        """
        Apply a code modification to a file.
        Requires approval before proceeding.
        
        Returns:
            (success, message)
        """
        logger.info(f"Applying modification to {file_path}")
        
        # Request approval if manager provided
        if approval_manager:
            import uuid
            request_id = str(uuid.uuid4())
            
            approved = await approval_manager.request_approval(
                request_id=request_id,
                description=f"Code Modification: {modification.description}",
                required_action="code_modification",
                details={
                    "file": file_path,
                    "type": modification.modification_type,
                    "original_lines": len(modification.original_code.splitlines()),
                    "new_lines": len(modification.modified_code.splitlines()),
                    "reasoning": modification.reasoning
                }
            )
            
            if not approved:
                logger.info(f"Modification rejected for {file_path}")
                return False, "User rejected modification"
        
        try:
            # Create backup
            file = Path(file_path)
            backup_path = f"{file_path}.backup"
            if file.exists():
                with open(file_path, 'r') as f:
                    original_content = f.read()
                self.rollback_stack.append({
                    "file": file_path,
                    "backup": backup_path,
                    "original_content": original_content
                })
            
            # Apply modification
            file.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(modification.modified_code)
            
            logger.info(f"Modification applied to {file_path}")
            self.modification_history.append({
                "file": file_path,
                "type": modification.modification_type,
                "timestamp": str(__import__('datetime').datetime.now())
            })
            
            return True, f"Modification applied successfully"
        
        except Exception as e:
            logger.error(f"Failed to apply modification: {str(e)}")
            return False, f"Error: {str(e)}"

    def rollback_last_modification(self) -> Tuple[bool, str]:
        """
        Rollback the last applied modification.
        """
        if not self.rollback_stack:
            return False, "No modifications to rollback"
        
        try:
            backup = self.rollback_stack.pop()
            with open(backup["file"], 'w') as f:
                f.write(backup["original_content"])
            
            logger.info(f"Rolled back {backup['file']}")
            return True, f"Rolled back {backup['file']}"
        
        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")
            return False, f"Rollback error: {str(e)}"

    def get_modification_history(self, limit: int = 50) -> list:
        """Get modification history"""
        return self.modification_history[-limit:]
