# Installation Guide - Phase 1

## Prerequisites

- **Python 3.10+** (https://www.python.org/downloads/)
- **Ollama** (optional, for local LLM) - https://ollama.ai
- **OpenAI API Key** (optional, for GPT-3.5 access)

## Step 1: Clone Repository

```bash
git clone https://github.com/y7217937891273987-lang-eg00/verbose-happiness.git
cd verbose-happiness
```

## Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Configure LLM

### Option A: Ollama (Recommended for Phase 1)

1. Download and install Ollama: https://ollama.ai
2. Run Ollama: `ollama serve`
3. Pull a model: `ollama pull mistral` (or `neural-chat`, `orca`)
4. Leave running in background

### Option B: OpenAI API

1. Get API key from https://openai.com/api/
2. Create `.env` file in project root:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
3. Update `config/settings.json`:
   ```json
   {
     "llm": {
       "primary_provider": "openai"
     }
   }
   ```

## Step 5: Run Application

```bash
python main.py
```

You'll see an interactive CLI with options to:
- Submit tasks
- View framework status
- View audit logs

## Troubleshooting

### "Ollama server not responding"
- Ensure Ollama is running: `ollama serve` in another terminal
- Check host: Default is `http://localhost:11434`

### "Module not found"
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

### "OpenAI API Error"
- Verify API key is correct
- Check your OpenAI account has credits

## Next Steps

- Read `README.md` for architecture overview
- Explore agent framework in `src/core/agent_framework.py`
- Check out sample tasks in Phase 1 examples

## Phase 1 Complete!

You now have:
- ✅ Agent framework with task decomposition
- ✅ LLM integration (Ollama + OpenAI option)
- ✅ Permission/approval system
- ✅ Audit logging for transparency
- ✅ CLI interface for testing

**Next: Phase 2 will add GUI, self-learning, and internet research capability.**
