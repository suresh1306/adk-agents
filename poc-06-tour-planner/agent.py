"""
POC 06: Tour Planner Agent with Groq + Sub Agents + Custom Tools

This demonstrates a comprehensive multi-agent tour planning system with specialized agents and custom tools.

To run this agent:
  adk run .               # Run in terminal
  adk web                 # Run in browser UI
  adk api_server          # Start API server
"""

from google.adk.agents import Agent
from google.adk.llms import LiteLlm
from tools import (
    search_destination,
    calculate_budget,
    create_itinerary,
    get_weather_info,
    get_travel_recommendations,
    calculate_travel_distance
)

# Create LiteLLM wrapper for Groq (shared by all agents)
groq_model = LiteLlm(model="groq/llama-3.3-70b-versatile")

# Create specialized sub-agents

# 1. Destination Research Agent
research_agent = Agent(
    name="destination_researcher",
    model=groq_model,
    description="Researches destinations, attractions, and points of interest",
    instruction="""You are a destination research specialist. Your expertise includes:
    - Finding information about tourist destinations
    - Identifying popular attractions and activities
    - Researching local culture and customs
    - Finding restaurants and accommodations

    Use the search_destination tool to gather information.
    Provide detailed, helpful insights about destinations.""",
    tools=[search_destination, calculate_travel_distance],
)

# 2. Budget Calculator Agent
budget_agent = Agent(
    name="budget_calculator",
    model=groq_model,
    description="Calculates travel budgets and cost estimates",
    instruction="""You are a budget planning specialist. Your expertise includes:
    - Estimating travel costs
    - Breaking down expenses (accommodation, food, activities, transport)
    - Providing cost-saving tips
    - Comparing budget options

    Use the calculate_budget tool for cost estimates.
    Help travelers understand and plan their expenses.""",
    tools=[calculate_budget],
)

# 3. Itinerary Builder Agent
itinerary_agent = Agent(
    name="itinerary_builder",
    model=groq_model,
    description="Creates detailed day-by-day travel itineraries",
    instruction="""You are an itinerary planning specialist. Your expertise includes:
    - Creating structured day-by-day plans
    - Balancing activities and rest time
    - Organizing activities by location and timing
    - Customizing plans based on traveler interests

    Use the create_itinerary tool to build schedules.
    Create practical, enjoyable itineraries.""",
    tools=[create_itinerary],
)

# 4. Weather Information Agent
weather_agent = Agent(
    name="weather_advisor",
    model=groq_model,
    description="Provides weather information and seasonal travel advice",
    instruction="""You are a weather and seasonal travel advisor. Your expertise includes:
    - Providing weather information for destinations
    - Suggesting best times to visit
    - Advising on what to pack based on weather
    - Seasonal travel recommendations

    Use the get_weather_info tool for weather data.
    Help travelers prepare for weather conditions.""",
    tools=[get_weather_info],
)

# 5. Recommendations Agent
recommendations_agent = Agent(
    name="travel_advisor",
    model=groq_model,
    description="Provides travel tips, recommendations, and advice",
    instruction="""You are a travel recommendations specialist. Your expertise includes:
    - Providing local tips and advice
    - Recommending activities and experiences
    - Cultural and safety guidance
    - Food and dining suggestions

    Use the get_travel_recommendations tool for tips.
    Enhance travelers' experiences with expert advice.""",
    tools=[get_travel_recommendations],
)

# Create the coordinator agent
root_agent = Agent(
    name="tour_planner_coordinator",
    model=groq_model,
    description="Coordinates comprehensive tour planning with specialized agents",
    instruction="""You are the Tour Planner Coordinator managing a team of travel specialists:

    1. Destination Researcher - for finding attractions and information
    2. Budget Calculator - for cost estimation and financial planning
    3. Itinerary Builder - for creating day-by-day schedules
    4. Weather Advisor - for weather information and seasonal advice
    5. Travel Advisor - for recommendations and tips

    Your role is to:
    - Understand traveler requirements (destination, duration, budget, interests)
    - Coordinate with appropriate specialists
    - Compile comprehensive travel plans
    - Ensure all aspects are covered (research, budget, schedule, weather, tips)

    Provide complete, well-organized tour plans that help travelers have amazing experiences.
    When planning a trip, engage multiple agents to cover all aspects.""",
    sub_agents=[
        research_agent,
        budget_agent,
        itinerary_agent,
        weather_agent,
        recommendations_agent
    ],
)
