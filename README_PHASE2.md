# Phase 2: GUI Interface & Self-Learning System

## Overview

Phase 2 adds the visual interface and self-improving capabilities:

1. **Desktop GUI** (PySimpleGUI) - Task submission, monitoring, approval dialogs
2. **Internet Research Agent** - Web search capability with your permission
3. **Self-Learning System** - Agent can suggest and apply code improvements
4. **Free LLM Fallback** - Integration with free API resources
5. **Enhanced Approval UI** - Visual approval workflows with detailed change previews

## New Components

### GUI System (`src/ui/`)
- `main_window.py` - Primary application window
- `task_panel.py` - Task input and submission
- `approval_dialog.py` - Visual approval interface
- `monitoring_panel.py` - Real-time task execution monitoring
- `dashboard.py` - System status and analytics

### Self-Learning System (`src/learning/`)
- `code_modifier.py` - Agent-driven code improvements
- `knowledge_learner.py` - Learn from task results
- `improvement_suggester.py` - Suggest enhancements

### Internet Capability (`src/internet/`)
- `web_search.py` - Search functionality
- `web_scraper.py` - Content extraction
- `free_llm_fallback.py` - Free API integration

## Installation & Running

```bash
# Checkout Phase 2
git checkout phase-2-gui-learning

# Install new GUI dependencies
pip install -r requirements.txt

# Run with GUI
python main_gui.py
```

## Key Features

### GUI Interface
- Clean, intuitive task submission
- Real-time monitoring of agent execution
- Visual approval dialogs with change preview
- System status dashboard
- Audit log viewer

### Self-Learning
- Agents analyze task results
- Suggest code improvements
- Request permission before applying changes
- Learn from successful task patterns

### Internet Research
- Search the web for information
- Extract and summarize content
- Fallback to free LLM APIs if needed
- Log all internet access for transparency

## Testing

```bash
# Run GUI
python main_gui.py

# Or CLI (Phase 1 mode)
python main.py
```

## Next: Phase 3
Business automation templates and deployment agents.
