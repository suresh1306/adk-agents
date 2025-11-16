# POC 02: Simple LLMAgent with Groq Provider

This POC demonstrates using a third-party LLM provider (Groq) with Google ADK via LiteLLM.

## Features

- Integration with Groq LLM provider using LiteLLM
- Uses Llama model via Groq
- Demonstrates model flexibility in ADK

## Setup

1. Install dependencies:
```bash
cd ..
pip install -r requirements.txt
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

- Creating an `LlmAgent` with LiteLLM integration
- Using Groq's hosted models (Llama 3.3 70B)
- Same ADK patterns work with different providers
- Runtime and session management with third-party LLMs

## Code Structure

- `agent.py` - Main agent implementation with LiteLLM configuration
- Uses `LiteLlm` wrapper to integrate Groq models
