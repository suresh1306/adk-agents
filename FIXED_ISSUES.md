# Issues Fixed and How to Run the Agents

## What Was Wrong

The original POC implementations had several critical issues due to using outdated/incorrect Google ADK API patterns:

### 1. **Incorrect Imports**
```python
# ❌ WRONG (these don't exist in google-adk)
from google.adk.runners import Runtime
from google.adk.services import SessionService
```

These classes don't exist in the current Google ADK Python library.

### 2. **Wrong Structure**
```python
# ❌ WRONG - Using main() function pattern
def main():
    agent = LlmAgent(...)
    runtime = Runtime(root_agent=agent)  # Doesn't exist!
    # ... interactive loop ...

if __name__ == "__main__":
    main()
```

Google ADK expects a different structure with `root_agent` at module level.

### 3. **Wrong Execution Method**
```bash
# ❌ WRONG
python agent.py
```

Google ADK agents should be run using the ADK CLI tools, not directly with Python.

## What's Fixed

### 1. **Correct Imports**
```python
# ✅ CORRECT
from google.adk.agents import Agent
from google.adk.llms import LiteLlm  # For non-Gemini models
```

### 2. **Correct Structure**
```python
# ✅ CORRECT - Define root_agent at module level
from google.adk.agents import Agent

root_agent = Agent(
    name="my_agent",
    model="gemini-2.0-flash-exp",
    description="What the agent does",
    instruction="How it should behave",
    tools=[my_tool_function],  # Pass functions directly
)
```

### 3. **Correct Execution Method**
```bash
# ✅ CORRECT - Use ADK CLI
cd poc-01-gemini-simple
adk run .               # Terminal interface
adk web                 # Browser UI
adk api_server          # API server
```

## How to Run Each POC

### POC 1: Simple Gemini Agent
```bash
cd poc-01-gemini-simple
export GOOGLE_API_KEY="your-google-api-key"
adk run .
```

### POC 2: Simple Groq Agent
```bash
cd poc-02-groq-simple
export GROQ_API_KEY="your-groq-api-key"
adk run .
```

### POC 3: Web Search Agent (Groq + Custom Tool)
```bash
cd poc-03-groq-websearch
export GROQ_API_KEY="your-groq-api-key"
adk run .
```
Try: "What's the latest news about AI?"

### POC 4: Calculator Agent (Groq + Custom Tool)
```bash
cd poc-04-groq-calculator
export GROQ_API_KEY="your-groq-api-key"
adk run .
```
Try: "Calculate the square root of 144"

### POC 5: Multi-Agent System (Groq + Sub-Agents)
```bash
cd poc-05-groq-subagents
export GROQ_API_KEY="your-groq-api-key"
adk run .
```
Try: "Search for Python tutorials and write a summary"

### POC 6: Tour Planner (Groq + 5 Sub-Agents + Multiple Tools)
```bash
cd poc-06-tour-planner
export GROQ_API_KEY="your-groq-api-key"
adk run .
```
Try: "Plan a 5-day trip to Paris for 2 people"

## ADK CLI Commands Explained

### `adk run .`
- Runs the agent in **terminal mode**
- Interactive chat in your command line
- Type messages and get responses
- Type 'exit' to quit
- **This is the recommended way for testing**

### `adk web`
- Starts a **web UI** at `http://localhost:8000`
- Nice graphical interface for chatting
- Better for demos and presentations
- Shows message history

### `adk api_server`
- Starts a **FastAPI server** at `http://localhost:8000`
- Provides REST API endpoints
- Swagger documentation at `http://localhost:8000/docs`
- Use for integrating with other applications
- **Note**: There's currently a Pydantic compatibility issue with MCP that causes errors in /docs, but the agent still works

## API Key Setup

### Option 1: Environment Variables (Recommended)
```bash
export GOOGLE_API_KEY="your-google-api-key"
export GROQ_API_KEY="your-groq-api-key"
```

### Option 2: .env File
Create a `.env` file in each POC directory:
```
GOOGLE_API_KEY=your-google-api-key-here
GROQ_API_KEY=your-groq-api-key-here
```

ADK will automatically load environment variables from `.env` files.

## Getting API Keys

### Google AI API Key (for POC-01)
1. Visit https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key

### Groq API Key (for POC-02 through POC-06)
1. Visit https://console.groq.com/
2. Sign up or sign in
3. Go to API Keys section
4. Create new API key
5. Copy the key

## Common Issues and Solutions

### Issue: "command not found: adk"
**Solution**:
```bash
pip install google-adk
# If in a virtual environment, make sure it's activated
```

### Issue: "Could not import Runtime" or "No module named google.adk.runners"
**Solution**: This error appeared with the old, incorrect code. The fixed version doesn't use these imports anymore. Just pull the latest changes.

### Issue: Pydantic errors with `adk api_server`
**Solution**: This is a known issue with MCP client session compatibility in the current version. The `/docs` endpoint may fail, but the agent itself works fine. Use `adk run .` or `adk web` instead for now.

### Issue: "GOOGLE_API_KEY not set" or "GROQ_API_KEY not set"
**Solution**:
```bash
export GOOGLE_API_KEY="your-actual-key-here"
# OR create a .env file in the POC directory
```

### Issue: "duckduckgo_search module not found"
**Solution**:
```bash
pip install duckduckgo-search
# Or from the root directory:
pip install -r requirements.txt
```

## Architecture Summary

All POCs now follow the correct Google ADK pattern:

1. **agent.py** - Contains `root_agent` definition at module level
2. **tools.py** (where applicable) - Contains tool functions
3. **README.md** - Instructions for that specific POC

The agent is run using the ADK CLI, which:
- Loads the `root_agent` from `agent.py`
- Handles session management automatically
- Provides multiple interfaces (terminal, web, API)
- Manages conversation state

## Testing the Agents

### Quick Test for POC-01:
```bash
cd poc-01-gemini-simple
export GOOGLE_API_KEY="your-key"
adk run .

# Then type:
You: Hello! What can you help me with?
# Press Enter and wait for response
```

### Quick Test for POC-06 (Most Advanced):
```bash
cd poc-06-tour-planner
export GROQ_API_KEY="your-key"
adk run .

# Then type:
You: Plan a 3-day trip to Tokyo for 2 people with a $2000 budget
# Press Enter and watch the multi-agent system coordinate the planning!
```

## What Each POC Demonstrates

1. **POC-01**: Basic single agent with Gemini
2. **POC-02**: Using third-party LLM (Groq) via LiteLLM
3. **POC-03**: Custom tool creation (web search)
4. **POC-04**: Multiple custom tools (calculator)
5. **POC-05**: Multi-agent system (3 specialized agents)
6. **POC-06**: Complex real-world app (5 agents, multiple tools)

## Next Steps

1. Start with POC-01 to understand the basics
2. Progress through POC-02 to learn LLM provider flexibility
3. Try POC-03 and POC-04 to learn custom tool creation
4. Explore POC-05 for multi-agent orchestration
5. Run POC-06 to see a complete, production-like system

All POCs are now working correctly with the proper Google ADK structure!
