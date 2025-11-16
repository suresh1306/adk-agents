# POC 01: Simple LLMAgent with Gemini LLM

This POC demonstrates a basic LLMAgent using Google's Gemini model.

## Features

- Uses Google ADK's native Gemini integration
- Simple conversational agent
- Demonstrates basic agent creation, runtime, and session management

## Setup

1. Install dependencies:
```bash
cd ..
pip install -r requirements.txt
```

2. Set your Google API key:
```bash
export GOOGLE_API_KEY="your-google-api-key"
```

## Running the Agent

```bash
python agent.py
```

## What's Demonstrated

- Creating an `LlmAgent` with Gemini model
- Setting up agent runtime
- Creating and managing sessions
- Sending messages and receiving responses
- Basic conversation loop

## Code Structure

- `agent.py` - Main agent implementation
- Uses Google ADK's `LlmAgent`, `Runtime`, and `SessionService` classes
