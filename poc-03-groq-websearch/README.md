# POC 03: LLMAgent with Groq + Custom Websearch Tool

This POC demonstrates creating a custom web search tool and integrating it with a Groq-powered agent.

## Features

- Custom web search tool using DuckDuckGo API
- Groq LLM integration via LiteLLM
- Function tool creation with ADK
- Agent uses the tool to answer questions with current information

## Setup

1. Install dependencies:
```bash
cd ..
pip install -r requirements.txt
pip install duckduckgo-search  # For web search functionality
```

2. Set your Groq API key:
```bash
export GROQ_API_KEY="your-groq-api-key"
```

## Running the Agent

```bash
python agent.py
```

## What's Demonstrated

- Creating custom tools with `FunctionTool`
- Proper function signatures and docstrings for LLM understanding
- Tool integration with `LlmAgent`
- Agent autonomously decides when to use the search tool
- Combining multiple capabilities (LLM reasoning + web search)

## Code Structure

- `agent.py` - Main agent implementation
- `tools.py` - Custom web search tool definition
- Uses DuckDuckGo for actual search implementation

## Example Queries

Try asking:
- "What's the latest news about AI?"
- "Search for information about quantum computing"
- "What are the current weather conditions in Paris?"
