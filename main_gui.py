#!/usr/bin/env python3
"""Main GUI Application - Phase 2"""

import asyncio
import logging
from src.utils import setup_logging
from src.config import Settings
from src.core import AgentFramework, LLMManager
from src.core.agent_framework import LLMProvider
from src.agents import ResearchAgent, CodeAgent, BusinessAgent
from src.permissions import ApprovalManager, AuditLog
from src.internet import WebSearch, WebScraper, FreeLLMFallback
from src.learning import CodeModifier, KnowledgeLearner, ImprovementSuggester
from src.ui import MainWindow
from src.ui.approval_dialog import ApprovalDialog


class HybridAIGUI:
    """Main GUI application for Phase 2"""

    def __init__(self):
        # Initialize logging
        setup_logging(level="INFO")
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.settings = Settings()
        self.logger.info("Settings loaded")
        
        # Initialize LLM Manager
        llm_config = self.settings.get_llm_config()
        provider = LLMProvider(llm_config['primary_provider'])
        
        self.llm_manager = LLMManager(
            primary_provider=provider,
            ollama_host=llm_config['ollama']['host'],
            ollama_model=llm_config['ollama']['model']
        )
        self.logger.info("LLM Manager initialized")
        
        # Initialize Agent Framework
        self.agent_framework = AgentFramework(llm_manager=self.llm_manager)
        self.logger.info("Agent Framework initialized")
        
        # Register agents
        self._register_agents()
        
        # Initialize permissions and audit
        self.approval_manager = ApprovalManager()
        self.audit_log = AuditLog()
        self.logger.info("Approval Manager and Audit Log initialized")
        
        # Initialize Phase 2 components
        self._initialize_phase2_components()
        
        # Initialize GUI
        self.main_window = MainWindow(app_instance=self)
        self.logger.info("GUI initialized")
        
        # Set callbacks
        self.agent_framework.set_approval_callback(self._approval_callback_gui)

    def _register_agents(self):
        """Register available agents"""
        if self.settings.get('agents.enable_research_agent'):
            agent = ResearchAgent(llm_manager=self.llm_manager)
            self.agent_framework.register_agent(agent)
            self.logger.info("Research Agent registered")
        
        if self.settings.get('agents.enable_code_agent'):
            agent = CodeAgent(llm_manager=self.llm_manager)
            self.agent_framework.register_agent(agent)
            self.logger.info("Code Agent registered")
        
        if self.settings.get('agents.enable_business_agent'):
            agent = BusinessAgent(llm_manager=self.llm_manager)
            self.agent_framework.register_agent(agent)
            self.logger.info("Business Agent registered")

    def _initialize_phase2_components(self):
        """Initialize Phase 2 components"""
        # Internet capabilities
        self.web_search = WebSearch(search_engine="duckduckgo")
        self.web_scraper = WebScraper()
        self.free_llm_fallback = FreeLLMFallback()
        self.logger.info("Internet components initialized")
        
        # Learning components
        self.knowledge_learner = KnowledgeLearner()
        self.code_modifier = CodeModifier(llm_manager=self.llm_manager)
        self.improvement_suggester = ImprovementSuggester(
            knowledge_learner=self.knowledge_learner,
            code_modifier=self.code_modifier
        )
        self.logger.info("Learning components initialized")

    async def _approval_callback_gui(self, approval_request):
        """
        GUI-based approval callback.
        Shows approval dialog instead of CLI prompt.
        """
        approved = ApprovalDialog.show_approval_dialog(
            title=approval_request.description,
            description=f"Action: {approval_request.required_action}",
            details=approval_request.details,
            action_type=approval_request.required_action
        )
        
        await self.approval_manager.respond_to_approval(
            approval_request.request_id,
            approved,
            reason="User decision via GUI"
        )
        
        self.audit_log.log_approval_request(
            request_id=approval_request.request_id,
            action=approval_request.required_action,
            approved=approved
        )
        
        return approved

    async def process_task(self, task_description: str) -> dict:
        """
        Process a task with Phase 2 enhancements.
        """
        self.logger.info(f"Processing task: {task_description}")
        
        try:
            # Decompose and execute
            plan = await self.agent_framework.decompose_and_execute(task_description)
            
            # Learn from results
            for task in plan.sub_tasks:
                if task.result:
                    await self.knowledge_learner.learn_from_task(
                        task.description,
                        task.result,
                        "unknown",
                        5.0,  # execution time
                        task.status.value == "completed"
                    )
            
            return {
                "plan_id": plan.plan_id,
                "status": "completed",
                "results": [task.result for task in plan.sub_tasks if task.status.value == "completed"]
            }
        
        except Exception as e:
            self.logger.error(f"Task processing failed: {str(e)}")
            return {"status": "failed", "error": str(e)}

    def run(self):
        """
        Run the GUI application.
        """
        self.main_window.show()
        self.main_window.run_event_loop()


async def main():
    """Main application function"""
    app = HybridAIGUI()
    app.run()


if __name__ == "__main__":
    import sys
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nApplication closed.")
        sys.exit(0)
