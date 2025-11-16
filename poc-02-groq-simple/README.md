# POC 02: Simple LLMAgent with Groq Provider

This POC demonstrates using a third-party LLM provider (Groq) with Google ADK via LiteLLM.

## Features

- Integration with Groq LLM provider using LiteLLM
- Uses Llama model via Groq
- Demonstrates model flexibility in ADK

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
cd poc-02-groq-simple
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

- Creating an `Agent` with LiteLLM integration
- Using Groq's hosted models (Llama 3.3 70B)
- Same ADK patterns work with different providers
- Model flexibility using LiteLLM wrapper

## Code Structure

- `agent.py` - Main agent implementation with `root_agent` definition
- Uses `LiteLlm` wrapper to integrate Groq models

## Troubleshooting

**Error: "GROQ_API_KEY not set"**
- Set the environment variable: `export GROQ_API_KEY="your-key"`
- Or create a `.env` file in this directory
