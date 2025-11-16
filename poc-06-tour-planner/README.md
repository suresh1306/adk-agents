# POC 06: Tour Planner Agent with Groq + Sub Agents + Custom Tools

This POC demonstrates a comprehensive multi-agent tour planning system with specialized agents and custom tools.

## Features

- Complex multi-agent architecture for tour planning
- Five specialized sub-agents:
  - Destination Research Agent (search destinations)
  - Budget Calculator Agent (cost estimation)
  - Itinerary Builder Agent (schedule planning)
  - Weather Agent (weather information)
  - Recommendations Agent (suggestions)
- Multiple custom tools for various tasks
- Groq LLM for all agents
- Coordinated workflow for complete tour planning

## Setup

1. Install dependencies:
```bash
cd ..
pip install -r requirements.txt
pip install duckduckgo-search requests  # For web search and API calls
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

- Complex multi-agent orchestration
- Specialized agents with domain expertise
- Multiple custom tools working together
- Task delegation and coordination
- End-to-end workflow (research → budget → itinerary → recommendations)
- Real-world application of ADK concepts

## Architecture

```
Tour Planner Coordinator
├── Destination Research Agent (web search, location info)
├── Budget Calculator Agent (cost estimation, currency conversion)
├── Itinerary Builder Agent (schedule creation, time management)
├── Weather Agent (weather data, seasonal info)
└── Recommendations Agent (activity suggestions, tips)
```

## Code Structure

- `agent.py` - Main multi-agent tour planning system
- `tools.py` - Custom tools for various planning tasks
- Comprehensive set of tools for travel planning

## Example Usage

Try planning a tour:
```
You: I want to plan a 5-day trip to Paris for 2 people with a budget of $3000

The system will:
1. Research Paris destinations and attractions
2. Calculate budget breakdown
3. Create a day-by-day itinerary
4. Check weather conditions
5. Provide recommendations for restaurants, activities, etc.
```

## Example Queries

- "Plan a 3-day trip to Tokyo for 2 people"
- "What's the budget for a week in London?"
- "Create an itinerary for Barcelona with focus on art and culture"
- "What's the weather like in Bali in December?"
- "Suggest activities for a family trip to New York"
