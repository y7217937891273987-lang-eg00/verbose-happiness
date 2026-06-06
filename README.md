# Hybrid AI System - Intelligent Task Automation & Business Builder

## Project Overview

A standalone desktop application that:
- **Decomposes any task** into sub-tasks and deploys specialized agents
- **Self-learns** with your permission (internet research, code generation)
- **Automates business creation** (e-commerce, services, content, consulting)
- **Runs locally** on your PC (Ollama + optional OpenAI)
- **Honest feedback** - tells you exactly what it needs vs. what it can do

## Phase 1: Core Foundation (Weeks 1-2)

### Components
1. **Agent Framework** - Task decomposition & multi-agent orchestration
2. **LLM Integration** - Ollama (local) + OpenAI fallback
3. **Permission System** - Approval workflows for code changes
4. **Core GUI** - Task submission, monitoring, settings
5. **Configuration** - Project structure, LLM selection, API keys

## Directory Structure

```
verbose-happiness/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── agent_framework.py       # Agent base classes & orchestration
│   │   ├── task_decomposer.py       # Task breakdown logic
│   │   └── llm_manager.py           # LLM routing (Ollama/OpenAI)
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py            # Abstract agent class
│   │   ├── research_agent.py        # Internet research capability
│   │   ├── code_agent.py            # Code generation & analysis
│   │   └── business_agent.py        # Business automation
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py           # Primary GUI (PyQt5/PySimpleGUI)
│   │   ├── task_panel.py            # Task submission interface
│   │   ├── approval_dialog.py       # Permission workflow UI
│   │   └── monitoring_panel.py      # Real-time task monitoring
│   ├── permissions/
│   │   ├── __init__.py
│   │   ├── approval_manager.py      # Approval workflow engine
│   │   └── audit_log.py             # Transparency & logging
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py              # Config management
│   │   └── defaults.py              # Default configurations
│   └── utils/
│       ├── __init__.py
│       ├── logger.py                # Logging system
│       └── validators.py            # Input validation
├── assets/
│   ├── icons/                       # GUI icons
│   └── styles/                      # CSS/theme files
├── models/
│   ├── knowledge_base.db            # Local SQLite database
│   └── task_history.db              # Task execution history
├── config/
│   ├── settings.json                # User settings (LLM choice, API keys)
│   └── default_config.json          # Default configuration template
├── requirements.txt                 # Python dependencies
├── main.py                          # Application entry point
├── setup.py                         # Package setup
└── LICENSE
```

## Tech Stack - Phase 1

- **Language**: Python 3.10+
- **GUI**: PySimpleGUI (lightweight, cross-platform) / PyQt5 (advanced)
- **LLM**: Ollama (local) + OpenAI API (optional)
- **Database**: SQLite (local knowledge base)
- **HTTP Client**: Requests (API calls)
- **Task Queue**: APScheduler (task scheduling)

## Installation & Running

```bash
# Clone repository
git clone https://github.com/y7217937891273987-lang-eg00/verbose-happiness.git
cd verbose-happiness

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## Phase 1 Deliverables

- ✅ Agent framework with task decomposition
- ✅ LLM manager (Ollama local + OpenAI option)
- ✅ Permission/approval system
- ✅ Basic GUI (task submission + monitoring)
- ✅ Configuration management
- ✅ Audit logging & transparency

## Next Phases

- **Phase 2**: Self-learning + internet research + code modification
- **Phase 3**: Business automation templates
- **Phase 4**: Installer (Inno Setup) + deployment

---

**Status**: Phase 1 - Foundation Building
