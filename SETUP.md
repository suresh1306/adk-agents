# Setup Guide for Google ADK Agent POCs

This guide will help you set up and run all the POC agents in this repository.

## Prerequisites

- **Python**: Version 3.10 or higher
- **pip**: Python package manager
- **API Keys**:
  - Google AI API key (for POC-01)
  - Groq API key (for POC-02 through POC-06)

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd adk-agents
```

## Step 2: Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `google-adk` - Google Agent Development Kit
- `litellm` - Multi-provider LLM support
- `requests` - HTTP library
- `python-dotenv` - Environment variable management
- `duckduckgo-search` - Web search functionality

## Step 4: Set Up API Keys

### Option 1: Using .env file (Recommended)

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API keys:
```bash
GOOGLE_API_KEY=your-google-api-key-here
GROQ_API_KEY=your-groq-api-key-here
```

3. Load environment variables in your shell:
```bash
# On Linux/Mac:
export $(cat .env | xargs)

# Or use python-dotenv in your code
```

### Option 2: Export directly

```bash
# For POC-01 (Gemini)
export GOOGLE_API_KEY="your-google-api-key"

# For POC-02 through POC-06 (Groq)
export GROQ_API_KEY="your-groq-api-key"
```

## Step 5: Get API Keys

### Google AI API Key (for Gemini)

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key

### Groq API Key

1. Go to [Groq Console](https://console.groq.com/)
2. Sign up or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key

## Step 6: Run Individual POCs

### POC-01: Simple LLMAgent with Gemini

```bash
cd poc-01-gemini-simple
python agent.py
```

### POC-02: Simple LLMAgent with Groq

```bash
cd poc-02-groq-simple
python agent.py
```

### POC-03: LLMAgent with Groq + Websearch

```bash
cd poc-03-groq-websearch
python agent.py
```

### POC-04: LLMAgent with Groq + Calculator

```bash
cd poc-04-groq-calculator
python agent.py
```

### POC-05: LLMAgent with Groq + Sub Agents

```bash
cd poc-05-groq-subagents
python agent.py
```

### POC-06: Tour Planner Agent

```bash
cd poc-06-tour-planner
python agent.py
```

## Troubleshooting

### Import Errors

If you get import errors:
```bash
pip install --upgrade google-adk litellm
```

### API Key Errors

Make sure your API keys are set:
```bash
# Check environment variables
echo $GOOGLE_API_KEY
echo $GROQ_API_KEY
```

### Module Not Found: duckduckgo_search

```bash
pip install duckduckgo-search
```

### LiteLLM Authentication Errors

Ensure your Groq API key is correctly set and valid:
```bash
export GROQ_API_KEY="your-actual-key-here"
```

## Project Structure

```
adk-agents/
├── README.md                       # Main documentation
├── SETUP.md                        # This file
├── requirements.txt                # Python dependencies
├── .env.example                    # Example environment file
├── .gitignore                      # Git ignore patterns
├── poc-01-gemini-simple/          # POC 1
│   ├── README.md
│   └── agent.py
├── poc-02-groq-simple/            # POC 2
│   ├── README.md
│   └── agent.py
├── poc-03-groq-websearch/         # POC 3
│   ├── README.md
│   ├── agent.py
│   └── tools.py
├── poc-04-groq-calculator/        # POC 4
│   ├── README.md
│   ├── agent.py
│   └── tools.py
├── poc-05-groq-subagents/         # POC 5
│   ├── README.md
│   ├── agent.py
│   └── tools.py
└── poc-06-tour-planner/           # POC 6
    ├── README.md
    ├── agent.py
    └── tools.py
```

## Next Steps

1. Start with POC-01 to understand basic agent creation
2. Progress through POC-02 to learn about LLM provider integration
3. Explore POC-03 and POC-04 for custom tool creation
4. Study POC-05 for multi-agent systems
5. Try POC-06 for a complete, real-world application

## Additional Resources

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Google ADK Python GitHub](https://github.com/google/adk-python)
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Groq Documentation](https://console.groq.com/docs)

## Support

For issues or questions:
- Check the individual POC README files
- Review Google ADK documentation
- Check GitHub issues in the google/adk-python repository
