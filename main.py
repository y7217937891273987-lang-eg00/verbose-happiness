#!/usr/bin/env python3
"""Main application entry point"""

import asyncio
import logging
from src.utils import setup_logging
from src.config import Settings
from src.core import AgentFramework, LLMManager
from src.core.agent_framework import LLMProvider
from src.agents import ResearchAgent, CodeAgent, BusinessAgent
from src.permissions import ApprovalManager, AuditLog


class HybridAI:
    """Main application class"""

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
        
        # Set approval callback
        self.agent_framework.set_approval_callback(self._approval_callback)

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

    async def _approval_callback(self, approval_request):
        """
        Callback for approval requests.
        Phase 1: Simple console UI
        Phase 2: GUI integration
        """
        print(f"\n{'='*60}")
        print(f"APPROVAL REQUIRED: {approval_request.description}")
        print(f"Action Type: {approval_request.required_action}")
        print(f"Details: {approval_request.details}")
        print(f"{'='*60}")
        
        response = input("\nApprove? (yes/no): ").strip().lower()
        approved = response in ['yes', 'y']
        
        await self.approval_manager.respond_to_approval(
            approval_request.request_id,
            approved,
            reason="User decision via CLI"
        )
        
        self.audit_log.log_approval_request(
            request_id=approval_request.request_id,
            action=approval_request.required_action,
            approved=approved
        )
        
        return approved

    async def process_task(self, task_description: str) -> dict:
        """
        Main entry point for processing a task.
        """
        self.logger.info(f"Processing task: {task_description}")
        
        try:
            result = await self.agent_framework.execute_with_agents(task_description)
            return result
        except Exception as e:
            self.logger.error(f"Task processing failed: {str(e)}")
            return {"status": "failed", "error": str(e)}

    def get_status(self) -> dict:
        """Get application status"""
        return {
            "framework": self.agent_framework.get_framework_status(),
            "llm": self.llm_manager.get_provider_info(),
            "pending_approvals": len(self.approval_manager.get_pending_requests())
        }


async def main():
    """Main application function"""
    print("\n" + "="*60)
    print("Hybrid AI System - Phase 1: Core Foundation")
    print("="*60 + "\n")
    
    # Initialize application
    app = HybridAI()
    
    # Print status
    print("Application Status:")
    status = app.get_status()
    print(f"  Agents registered: {status['framework']['total_agents']}")
    print(f"  LLM Provider: {status['llm']['primary_provider']}")
    print()
    
    # Interactive CLI loop
    while True:
        print("\nOptions:")
        print("1. Submit a task")
        print("2. View framework status")
        print("3. View audit log")
        print("4. Exit")
        print()
        
        choice = input("Select option (1-4): ").strip()
        
        if choice == "1":
            task = input("\nEnter task description: ").strip()
            if task:
                print("\nProcessing task...")
                result = await app.process_task(task)
                print(f"\nResult: {result}")
        
        elif choice == "2":
            status = app.get_status()
            print(f"\nFramework Status:")
            print(f"  Total Agents: {status['framework']['total_agents']}")
            print(f"  Active Plans: {status['framework']['active_plans']}")
            print(f"  Pending Approvals: {status['pending_approvals']}")
        
        elif choice == "3":
            logs = app.audit_log.get_log_summary(limit=5)
            print("\nRecent Audit Log Entries:")
            for log in logs:
                print(f"  [{log['timestamp']}] {log['action_type']}: {log['description']}")
        
        elif choice == "4":
            print("\nExiting...")
            break
        
        else:
            print("Invalid option")


if __name__ == "__main__":
    asyncio.run(main())
