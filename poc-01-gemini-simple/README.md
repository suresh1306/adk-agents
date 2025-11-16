# POC 01: Simple LLMAgent with Gemini LLM

This POC demonstrates a basic LLMAgent using Google's Gemini model.

## Features

- Uses Google ADK's native Gemini integration
- Simple conversational agent
- Demonstrates basic agent creation using ADK CLI

## Setup

1. Install dependencies (from the root directory):
```bash
cd ..
pip install -r requirements.txt
```

2. Set your Google API key:
```bash
export GOOGLE_API_KEY="your-google-api-key"
```

Or create a `.env` file in this directory:
```
GOOGLE_API_KEY=your-google-api-key
```

## Running the Agent

Navigate to this directory first:
```bash
cd poc-01-gemini-simple
```

### Option 1: Terminal Interface (Recommended for beginners)
```bash
adk run .
```

This starts an interactive chat session in your terminal.

### Option 2: Web Browser UI
```bash
adk web
```

This opens a web interface in your browser at `http://localhost:8000`

### Option 3: API Server
```bash
adk api_server
```

This starts a FastAPI server that you can interact with via HTTP requests or the Swagger UI at `http://localhost:8000/docs`

## What's Demonstrated

- Creating an `Agent` with Gemini model
- Basic agent configuration (name, model, description, instruction)
- Using ADK CLI to run agents
- Interactive conversation with the agent

## Code Structure

- `agent.py` - Main agent implementation with `root_agent` definition
- Uses Google ADK's `Agent` class

## Example Usage

```bash
$ adk run .
Chat with gemini_assistant (type 'exit' to quit)
You: What can you help me with?
Agent: I can help you with various tasks like answering questions,
       providing information, helping with code, and much more!
```

## Troubleshooting

**Error: "GOOGLE_API_KEY not set"**
- Set the environment variable: `export GOOGLE_API_KEY="your-key"`
- Or create a `.env` file in this directory

**Error: "command not found: adk"**
- Make sure google-adk is installed: `pip install google-adk`
- Activate your virtual environment if using one

**Error: "Model not found"**
- Verify your API key is valid
- Try using `gemini-2.5-flash` instead of `gemini-2.0-flash-exp`
