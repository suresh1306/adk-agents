# Quick Start Guide

Get started with Google ADK Python agents in 5 minutes!

## Quick Setup

```bash
# 1. Install dependencies
python -m venv venv
source venv/bin/activate # or venv\Scripts\activate.bat on Windows
pip install -r requirements.txt

# 2. Set API keys
export GOOGLE_API_KEY="your-google-key"
export GROQ_API_KEY="your-groq-key"

# 3. Run a POC
cd poc-01-gemini-simple
adk run .
```

## POC Overview

### POC 1: Gemini Basic Agent
**What it does**: Simple conversational agent with Gemini
**Run**: `cd poc-01-gemini-simple && adk run .`
**Key concept**: Basic Agent with Google's native model

### POC 2: Groq Basic Agent
**What it does**: Simple conversational agent with Groq
**Run**: `cd poc-02-groq-simple && adk run .`
**Key concept**: Using LiteLLM for third-party providers

### POC 3: Web Search Agent
**What it does**: Agent that can search the web
**Run**: `cd poc-03-groq-websearch && adk run .`
**Key concept**: Creating custom tools as Python functions
**Try**: "What's the latest news about AI?"

### POC 4: Calculator Agent
**What it does**: Agent that performs calculations
**Run**: `cd poc-04-groq-calculator && adk run .`
**Key concept**: Multiple custom tools, safe code execution
**Try**: "Calculate the square root of 144"

### POC 5: Multi-Agent System
**What it does**: Coordinator with 3 specialized sub-agents
**Run**: `cd poc-05-groq-subagents && adk run .`
**Key concept**: Sub-agents, task delegation
**Try**: "Search for Python tutorials and summarize"

### POC 6: Tour Planner (Most Advanced)
**What it does**: Complete tour planning with 5 specialized agents
**Run**: `cd poc-06-tour-planner && adk run .`
**Key concept**: Complex multi-agent orchestration
**Try**: "Plan a 5-day trip to Paris for 2 people"

## Running Options

Each POC supports three ways to run:

### 1. Terminal Interface (Recommended)
```bash
cd poc-XX-name
adk run .
```
Interactive chat in your terminal. Type your message and press Enter.

### 2. Web Browser UI
```bash
cd poc-XX-name
adk web
```
Opens a web interface at `http://localhost:8000` with a chat UI.

### 3. API Server
```bash
cd poc-XX-name
adk api_server
```
Starts a FastAPI server. Access Swagger docs at `http://localhost:8000/docs`

## Key Components

### Creating an Agent (Correct Pattern)
```python
from google.adk.agents import Agent

# Define root_agent at module level (required by ADK)
root_agent = Agent(
    name="my_agent",
    model="gemini-2.0-flash-exp",  # or LiteLlm(model="groq/...")
    description="What the agent does",
    instruction="How the agent should behave"
)
```

### Adding Tools
```python
# Define tool as a regular Python function
def my_tool(param: str) -> dict:
    """Tool description for the LLM."""
    return {"result": "value"}

# Pass function directly to Agent
root_agent = Agent(
    ...,
    tools=[my_tool]  # Just pass the function!
)
```

### Adding Sub-Agents
```python
specialist1 = Agent(name="specialist1", ...)
specialist2 = Agent(name="specialist2", ...)

root_agent = Agent(
    name="coordinator",
    sub_agents=[specialist1, specialist2],
    ...
)
```

## Common Patterns

### Pattern 1: Single Agent with Tools
See: POC-03, POC-04
- Create custom tools as Python functions
- Pass them to the `tools=[]` parameter
- Agent automatically uses them when needed

### Pattern 2: Multi-Agent System
See: POC-05, POC-06
- Create specialized agents with specific tools
- Create coordinator with `sub_agents=[]`
- Coordinator delegates to specialists

### Pattern 3: Using Different LLM Providers
See: POC-01 (Gemini), POC-02+ (Groq)
- Gemini: Direct model string `"gemini-2.0-flash-exp"`
- Other providers: `LiteLlm(model="groq/llama-3.3-70b-versatile")`

## API Keys

### Get Google AI Key
1. Visit: https://makersuite.google.com/app/apikey
2. Create API Key
3. `export GOOGLE_API_KEY="key"`

### Get Groq Key
1. Visit: https://console.groq.com/
2. Create API Key
3. `export GROQ_API_KEY="key"`

## Troubleshooting

**"command not found: adk"**
```bash
pip install google-adk
# Then restart your terminal or activate your venv
```

**"Module not found"**
```bash
pip install --upgrade google-adk litellm duckduckgo-search
```

**"API key not set"**
```bash
export GOOGLE_API_KEY="your-key"
export GROQ_API_KEY="your-key"
```

**"Could not import Runtime" or similar**
- The old code structure was incorrect
- All POCs are now fixed
- Use `adk run .` NOT `python agent.py`

## Next Steps

1. ✅ Run POC-01 to understand basics: `cd poc-01-gemini-simple && adk run .`
2. ✅ Run POC-02 to see LiteLLM integration
3. ✅ Run POC-03/04 to learn custom tools
4. ✅ Run POC-05 to explore multi-agent systems
5. ✅ Run POC-06 for complete application example
6. 📚 Read [full documentation](https://google.github.io/adk-docs/)
7. 🔨 Build your own agent!

## Resources

- 📖 [Setup Guide](SETUP.md) - Detailed setup instructions
- 📘 [Main README](README.md) - Full project documentation
- 🌐 [Google ADK Docs](https://google.github.io/adk-docs/)
- 💻 [ADK Python GitHub](https://github.com/google/adk-python)
