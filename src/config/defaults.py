"""Default configuration values"""

DEFAULT_CONFIG = {
    "llm": {
        "primary_provider": "ollama",  # Options: 'ollama', 'openai', 'free_api'
        "ollama": {
            "host": "http://localhost:11434",
            "model": "mistral"  # or 'neural-chat', 'orca', 'llama2'
        },
        "openai": {
            "api_key": "",  # User must provide
            "model": "gpt-3.5-turbo"
        }
    },
    "gui": {
        "theme": "dark",  # Options: 'dark', 'light'
        "window_width": 1200,
        "window_height": 800,
        "show_detailed_logs": True
    },
    "approval": {
        "require_approval_for_code": True,
        "require_approval_for_internet": True,
        "require_approval_for_business_setup": True,
        "approval_timeout_seconds": 3600
    },
    "database": {
        "path": "models/knowledge_base.db",
        "task_history_path": "models/task_history.db"
    },
    "logging": {
        "level": "INFO",  # DEBUG, INFO, WARNING, ERROR
        "audit_log_path": "logs/audit.log"
    },
    "agents": {
        "enable_research_agent": True,
        "enable_code_agent": True,
        "enable_business_agent": True
    },
    "business": {
        "auto_detect_opportunities": False,
        "supported_types": ["ecommerce", "service", "content", "consulting"]
    }
}
