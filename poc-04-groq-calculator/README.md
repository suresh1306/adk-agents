# POC 04: LLMAgent with Groq + Custom Calculator Tool

This POC demonstrates creating custom calculator tools and integrating them with a Groq-powered agent.

## Features

- Multiple custom calculator tools (basic math, advanced functions)
- Groq LLM integration via LiteLLM
- Safe expression evaluation
- Agent uses tools for mathematical computations

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
cd poc-04-groq-calculator
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

- Creating multiple custom tools
- Safe mathematical expression evaluation
- Advanced math functions (trigonometry, logarithms, etc.)
- Tool composition and selection by the agent
- Structured return values for better agent understanding

## Code Structure

- `agent.py` - Main agent implementation with `root_agent` definition
- `tools.py` - Custom calculator tool definitions
- Includes basic arithmetic and advanced mathematical functions

## Example Queries

Try asking:
- "What is 123 * 456?"
- "Calculate the square root of 144"
- "What is sin(45 degrees)?"
- "Calculate 2^10"
