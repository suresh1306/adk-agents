# Google ADK Python Agent POCs

This repository contains multiple proof-of-concept (POC) implementations using Google's Agent Development Kit (ADK) for Python.

## Overview

Google ADK is an open-source, code-first Python toolkit for building, evaluating, and deploying sophisticated AI agents with flexibility and control.

## POCs Included

1. **POC-01: Simple LLMAgent with Gemini LLM** (`poc-01-gemini-simple/`)
   - Basic agent using Google's Gemini model
   - Demonstrates core ADK concepts

2. **POC-02: Simple LLMAgent with Groq Provider** (`poc-02-groq-simple/`)
   - Agent using Groq LLM provider via LiteLLM
   - Shows integration with third-party LLM providers

3. **POC-03: LLMAgent with Groq + Custom Websearch Tool** (`poc-03-groq-websearch/`)
   - Groq-powered agent with custom web search functionality
   - Demonstrates custom tool creation

4. **POC-04: LLMAgent with Groq + Custom Calculator Tool** (`poc-04-groq-calculator/`)
   - Groq-powered agent with calculator capabilities
   - Shows function tool implementation

5. **POC-05: LLMAgent with Groq + Sub Agents** (`poc-05-groq-subagents/`)
   - Multi-agent system with Groq
   - Demonstrates agent orchestration and delegation

6. **POC-06: Tour Planner Agent** (`poc-06-tour-planner/`)
   - Complex tour planning system
   - Combines sub-agents, custom tools, and advanced orchestration

## Prerequisites

- Python 3.10 or higher
- pip package manager
- API Keys:
  - Google AI API key (for Gemini models)
  - Groq API key (for Groq models)

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export GOOGLE_API_KEY="your-google-api-key"
export GROQ_API_KEY="your-groq-api-key"
```

## Running POCs

Each POC can be run independently. Navigate to the respective folder and follow the instructions in the folder's README.

Example:
```bash
cd poc-01-gemini-simple
python agent.py
```

## Documentation

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Google ADK Python GitHub](https://github.com/google/adk-python)
- [Google ADK Samples](https://github.com/google/adk-samples)

## License

Apache 2.0
