# POC 05: LLMAgent with Groq + Sub Agents

This POC demonstrates a multi-agent system with a coordinator agent and specialized sub-agents.

## Features

- Multi-agent architecture with coordinator pattern
- Three specialized sub-agents:
  - Research Agent (web search)
  - Math Agent (calculations)
  - Writer Agent (content creation)
- Groq LLM for all agents
- Automatic task delegation based on query type

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

## Running the Agent

Navigate to this directory first:
```bash
cd poc-05-groq-subagents
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

- Creating multiple specialized `Agent` instances
- Composing agents into a hierarchy with `sub_agents`
- Coordinator agent delegates tasks to appropriate specialists
- Each sub-agent has its own tools and expertise
- Inter-agent communication and orchestration

## Architecture

```
Coordinator Agent (Main)
├── Research Agent (web search tool)
├── Math Agent (calculator tools)
└── Writer Agent (content creation)
```

## Code Structure

- `agent.py` - Main multi-agent system with `root_agent` definition
- `tools.py` - Shared tools for sub-agents
- Each agent has specific instructions and capabilities

## Example Queries

Try asking:
- "Search for the latest AI news and summarize it" (Research Agent)
- "Calculate the compound interest on $10000 at 5% for 10 years" (Math Agent)
- "Write a short poem about technology" (Writer Agent)
- "Find information about Python and create a summary" (Research + Writer)
