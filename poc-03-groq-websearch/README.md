# POC 03: LLMAgent with Groq + Custom Websearch Tool

This POC demonstrates creating a custom web search tool and integrating it with a Groq-powered agent.

## Features

- Custom web search tool using DuckDuckGo API
- Groq LLM integration via LiteLLM
- Function tool creation with ADK
- Agent uses the tool to answer questions with current information

## Setup

1. Install dependencies (from the root directory):
```bash
cd ..
pip install -r requirements.txt
```

2. Set your Groq API key:
```bash
export GROQ_API_KEY="your-groq-api-key"
```

Or create a `.env` file in this directory:
```
GROQ_API_KEY=your-groq-api-key
```

## Running the Agent

Navigate to this directory first:
```bash
cd poc-03-groq-websearch
```

### Option 1: Terminal Interface (Recommended)
```bash
adk run .
```

### Option 2: Web Browser UI
```bash
adk web
```

### Option 3: API Server
```bash
adk api_server
```

## What's Demonstrated

- Creating custom tools as Python functions
- Proper function signatures and docstrings for LLM understanding
- Tool integration with `Agent`
- Agent autonomously decides when to use the search tool
- Combining multiple capabilities (LLM reasoning + web search)

## Code Structure

- `agent.py` - Main agent implementation with `root_agent` definition
- `tools.py` - Custom web search tool definition
- Uses DuckDuckGo for actual search implementation

## Example Queries

Try asking:
- "What's the latest news about AI?"
- "Search for information about quantum computing"
- "What are the current weather conditions in Paris?"

## Troubleshooting

**Error: "duckduckgo_search module not found"**
- Install it: `pip install duckduckgo-search`
