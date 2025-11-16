"""
POC 06: Tour Planner Agent with ADK Session and State Management

This demonstrates a comprehensive multi-agent tour planning system with:
- Specialized agents with output_key for state persistence
- ToolContext integration for stateful tools
- State templating for context-aware instructions
- Proper ADK session and state management

To run this agent:
  adk run .               # Run in terminal
  adk web                 # Run in browser UI
  adk api_server          # Start API server
"""

from datetime import datetime
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from tools import (
    search_destination,
    calculate_budget,
    create_itinerary,
    get_weather_info,
    get_travel_recommendations,
    calculate_travel_distance
)

# Get current date for context awareness
CURRENT_DATE = datetime.now().strftime("%B %d, %Y")
CURRENT_YEAR = datetime.now().year

# Create LiteLLM wrapper for Groq (shared by all agents)
groq_model = LiteLlm(model="groq/llama-3.3-70b-versatile")

# Create specialized sub-agents with output_key for state persistence

# 1. Destination Research Agent
research_agent = Agent(
    name="destination_researcher",
    model=groq_model,
    description="Researches destinations, attractions, and points of interest",
    instruction=f"""You are a destination research specialist. Your expertise includes:
    - Finding information about tourist destinations
    - Identifying popular attractions and activities
    - Researching local culture and customs
    - Finding restaurants and accommodations

    IMPORTANT CONTEXT:
    - Current date: {CURRENT_DATE}
    - Current year: {CURRENT_YEAR}
    - Provide current, up-to-date travel information relevant to {CURRENT_YEAR}
    - Do NOT reference outdated COVID-19 pandemic restrictions from 2020-2022
    - Focus on current travel requirements, visa policies, and safety guidelines

    STATEFUL CONTEXT AWARENESS:
    {{temp:destination?}} - Currently researching destination (if set)
    {{temp:travel_origin?}} - Traveler's origin location (if set)

    Use the search_destination and calculate_travel_distance tools to gather information.
    Provide detailed, helpful insights about destinations with current, relevant information.""",
    tools=[search_destination, calculate_travel_distance],
    output_key="research_summary"  # Saves response to state["research_summary"]
)

# 2. Budget Calculator Agent
budget_agent = Agent(
    name="budget_calculator",
    model=groq_model,
    description="Calculates travel budgets and cost estimates",
    instruction=f"""You are a budget planning specialist. Your expertise includes:
    - Estimating travel costs
    - Breaking down expenses (accommodation, food, activities, transport)
    - Providing cost-saving tips
    - Comparing budget options

    STATEFUL CONTEXT AWARENESS:
    {{temp:destination?}} - Trip destination (if set)
    {{temp:num_days?}} - Number of days (if set)
    {{temp:num_people?}} - Number of travelers (if set)
    {{user:accommodation_preference?}} - User's preferred accommodation type (if set)

    Use the calculate_budget tool for cost estimates.
    Reference previous context from state when available.
    Help travelers understand and plan their expenses.""",
    tools=[calculate_budget],
    output_key="budget_plan"  # Saves response to state["budget_plan"]
)

# 3. Itinerary Builder Agent
itinerary_agent = Agent(
    name="itinerary_builder",
    model=groq_model,
    description="Creates detailed day-by-day travel itineraries",
    instruction=f"""You are an itinerary planning specialist. Your expertise includes:
    - Creating structured day-by-day plans
    - Balancing activities and rest time
    - Organizing activities by location and timing
    - Customizing plans based on traveler interests

    STATEFUL CONTEXT AWARENESS:
    {{temp:destination?}} - Trip destination (if set)
    {{temp:num_days?}} - Number of days (if set)
    {{temp:interests?}} - Traveler's interests (if set)
    {{user:travel_interests?}} - User's general travel interests (if set)
    {{temp:total_budget?}} - Total trip budget (if calculated)

    Use the create_itinerary tool to build schedules.
    Reference destination and interests from state when available.
    Create practical, enjoyable itineraries that align with the budget.""",
    tools=[create_itinerary],
    output_key="itinerary_plan"  # Saves response to state["itinerary_plan"]
)

# 4. Weather Information Agent
weather_agent = Agent(
    name="weather_advisor",
    model=groq_model,
    description="Provides weather information and seasonal travel advice",
    instruction=f"""You are a weather and seasonal travel advisor. Your expertise includes:
    - Providing weather information for destinations
    - Suggesting best times to visit
    - Advising on what to pack based on weather
    - Seasonal travel recommendations

    IMPORTANT CONTEXT:
    - Current date: {CURRENT_DATE}
    - When providing seasonal advice, consider the current time of year
    - Provide relevant packing suggestions for the current or upcoming season

    STATEFUL CONTEXT AWARENESS:
    {{temp:destination?}} - Trip destination (if set)

    Use the get_weather_info tool for weather data.
    Reference destination from state when available.
    Help travelers prepare for weather conditions.""",
    tools=[get_weather_info],
    output_key="weather_advice"  # Saves response to state["weather_advice"]
)

# 5. Recommendations Agent
recommendations_agent = Agent(
    name="travel_advisor",
    model=groq_model,
    description="Provides travel tips, recommendations, and advice",
    instruction=f"""You are a travel recommendations specialist. Your expertise includes:
    - Providing local tips and advice
    - Recommending activities and experiences
    - Cultural and safety guidance
    - Food and dining suggestions

    STATEFUL CONTEXT AWARENESS:
    {{temp:destination?}} - Trip destination (if set)
    {{user:travel_interests?}} - User's travel interests (if set)

    Use the get_travel_recommendations tool for tips.
    Personalize recommendations based on user interests from state.
    Enhance travelers' experiences with expert advice.""",
    tools=[get_travel_recommendations],
    output_key="travel_tips"  # Saves response to state["travel_tips"]
)

# Create the coordinator agent with comprehensive state awareness
root_agent = Agent(
    name="tour_planner_coordinator",
    model=groq_model,
    description="Coordinates comprehensive tour planning with specialized agents and state management",
    instruction=f"""You are the Tour Planner Coordinator managing a team of travel specialists:

    1. Destination Researcher - for finding attractions and information
    2. Budget Calculator - for cost estimation and financial planning
    3. Itinerary Builder - for creating day-by-day schedules
    4. Weather Advisor - for weather information and seasonal advice
    5. Travel Advisor - for recommendations and tips

    IMPORTANT CONTEXT:
    - Current date: {CURRENT_DATE}
    - Current year: {CURRENT_YEAR}
    - Ensure all information provided is current and relevant to {CURRENT_YEAR}
    - Do NOT reference outdated pandemic-era travel restrictions
    - Provide modern, up-to-date travel planning assistance

    SESSION STATE AWARENESS:
    You have access to the full conversation state. Reference previous planning work:

    Trip Planning State (temp: scope - current trip):
    - {{temp:destination?}} - Destination being planned
    - {{temp:num_days?}} - Number of days
    - {{temp:num_people?}} - Number of travelers
    - {{temp:travel_origin?}} - Traveler's origin location
    - {{temp:total_budget?}} - Calculated total budget
    - {{temp:interests?}} - Current trip interests

    User Preferences (user: scope - persists across sessions):
    - {{user:accommodation_preference?}} - Preferred accommodation type
    - {{user:travel_interests?}} - General travel interests

    Previous Agent Responses (saved via output_key):
    - {{research_summary?}} - Latest destination research
    - {{budget_plan?}} - Latest budget calculation
    - {{itinerary_plan?}} - Latest itinerary created
    - {{weather_advice?}} - Latest weather information
    - {{travel_tips?}} - Latest travel recommendations

    Your role is to:
    - Understand traveler requirements (destination, duration, budget, interests)
    - Coordinate with appropriate specialists
    - REFERENCE PREVIOUS WORK: Use state to avoid redundant questions
    - Build upon previous responses saved in state
    - Compile comprehensive travel plans
    - Ensure all aspects are covered (research, budget, schedule, weather, tips)

    CONVERSATION FLOW:
    1. When user mentions a destination, coordinate with research_agent
    2. When budget details are discussed, use budget_agent
    3. Once basics are set, create itinerary with itinerary_agent
    4. Provide weather context with weather_agent
    5. Enhance with recommendations from travel_advisor

    INTELLIGENT CONTEXT USAGE:
    - If {{temp:destination?}} is set, reference it instead of asking again
    - If {{budget_plan?}} exists, build upon it rather than recalculating
    - If {{user:travel_interests?}} are known, use them to personalize suggestions
    - Always check state before delegating to sub-agents to avoid redundancy

    Provide complete, well-organized tour plans that help travelers have amazing experiences.
    Be conversational, reference previous context, and build on what's already been discussed.""",
    sub_agents=[
        research_agent,
        budget_agent,
        itinerary_agent,
        weather_agent,
        recommendations_agent
    ],
)
