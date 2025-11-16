# Quick Start Guide

Get started with Google ADK Python agents in 5 minutes!

## Quick Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set API keys
export GOOGLE_API_KEY="your-google-key"
export GROQ_API_KEY="your-groq-key"

# 3. Run a POC
cd poc-01-gemini-simple
python agent.py
```

## POC Overview

### POC 1: Gemini Basic Agent
**What it does**: Simple conversational agent with Gemini
**Run**: `cd poc-01-gemini-simple && python agent.py`
**Key concept**: Basic LlmAgent with Google's native model

### POC 2: Groq Basic Agent
**What it does**: Simple conversational agent with Groq
**Run**: `cd poc-02-groq-simple && python agent.py`
**Key concept**: Using LiteLLM for third-party providers

### POC 3: Web Search Agent
**What it does**: Agent that can search the web
**Run**: `cd poc-03-groq-websearch && python agent.py`
**Key concept**: Creating custom tools with FunctionTool
**Try**: "What's the latest news about AI?"

### POC 4: Calculator Agent
**What it does**: Agent that performs calculations
**Run**: `cd poc-04-groq-calculator && python agent.py`
**Key concept**: Multiple custom tools, safe code execution
**Try**: "Calculate the square root of 144"

### POC 5: Multi-Agent System
**What it does**: Coordinator with 3 specialized sub-agents
**Run**: `cd poc-05-groq-subagents && python agent.py`
**Key concept**: Sub-agents, task delegation
**Try**: "Search for Python tutorials and summarize"

### POC 6: Tour Planner (Most Advanced)
**What it does**: Complete tour planning with 5 specialized agents
**Run**: `cd poc-06-tour-planner && python agent.py`
**Key concept**: Complex multi-agent orchestration
**Try**: "Plan a 5-day trip to Paris for 2 people"

## Key Components

### Creating an Agent
```python
from google.adk.agents import LlmAgent

agent = LlmAgent(
    name="my_agent",
    model="gemini-2.0-flash-exp",  # or LiteLlm(model="groq/...")
    description="What the agent does",
    instruction="How the agent should behave"
)
```

### Adding Tools
```python
from google.adk.tools import FunctionTool

def my_tool(param: str) -> dict:
    """Tool description for the LLM."""
    return {"result": "value"}

tool = FunctionTool(my_tool)
agent = LlmAgent(..., tools=[tool])
```

### Adding Sub-Agents
```python
specialist1 = LlmAgent(name="specialist1", ...)
specialist2 = LlmAgent(name="specialist2", ...)

coordinator = LlmAgent(
    name="coordinator",
    sub_agents=[specialist1, specialist2],
    ...
)
```

### Running the Agent
```python
from google.adk.runners import Runtime
from google.adk.services import SessionService

runtime = Runtime(root_agent=agent)
session_service = SessionService(runtime=runtime)
session = session_service.create_session()

response = session_service.send(
    session_id=session.id,
    message="Hello!"
)
print(response.content)
```

## Common Patterns

### Pattern 1: Single Agent with Tools
See: POC-03, POC-04
- Create custom tools
- Add to agent's tools list
- Agent automatically uses them when needed

### Pattern 2: Multi-Agent System
See: POC-05, POC-06
- Create specialized agents with specific tools
- Create coordinator with sub_agents
- Coordinator delegates to specialists

### Pattern 3: Using Different LLM Providers
See: POC-01 (Gemini), POC-02+ (Groq)
- Gemini: Direct model string
- Other providers: LiteLlm wrapper

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

**"Module not found"**
```bash
pip install --upgrade google-adk litellm duckduckgo-search
```

**"API key not set"**
```bash
export GOOGLE_API_KEY="your-key"
export GROQ_API_KEY="your-key"
```

**"Import error: google.adk"**
```bash
pip install google-adk
```

## Next Steps

1. ✅ Run POC-01 to understand basics
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
