#!/usr/bin/env python3
"""
POC 06: Tour Planner Agent with Groq + Sub Agents + Custom Tools

This demonstrates a comprehensive tour planning system with multiple specialized agents.
"""

import os
from google.adk.agents import LlmAgent
from google.adk.runners import Runtime
from google.adk.services import SessionService
from google.adk.llms import LiteLlm
from google.adk.tools import FunctionTool
from tools import (
    search_destination,
    calculate_budget,
    create_itinerary,
    get_weather_info,
    get_travel_recommendations,
    calculate_travel_distance
)


def main():
    """Main function to run the tour planner multi-agent system."""

    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY environment variable not set")
        print("Please set it with: export GROQ_API_KEY='your-api-key'")
        return

    print("=" * 70)
    print("POC 06: Tour Planner - Multi-Agent System with Custom Tools")
    print("=" * 70)
    print()

    # Create LiteLLM wrapper for Groq
    groq_model = LiteLlm(model="groq/llama-3.3-70b-versatile")

    print("✓ LiteLLM model configured for Groq")
    print()

    # Create tools
    search_tool = FunctionTool(search_destination)
    budget_tool = FunctionTool(calculate_budget)
    itinerary_tool = FunctionTool(create_itinerary)
    weather_tool = FunctionTool(get_weather_info)
    recommendations_tool = FunctionTool(get_travel_recommendations)
    distance_tool = FunctionTool(calculate_travel_distance)

    print("✓ Custom tools created")
    print()

    # Create specialized sub-agents

    # 1. Destination Research Agent
    research_agent = LlmAgent(
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
        tools=[search_tool, distance_tool],
    )

    print("✓ Destination Research Agent created")

    # 2. Budget Calculator Agent
    budget_agent = LlmAgent(
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
        tools=[budget_tool],
    )

    print("✓ Budget Calculator Agent created")

    # 3. Itinerary Builder Agent
    itinerary_agent = LlmAgent(
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
        tools=[itinerary_tool],
    )

    print("✓ Itinerary Builder Agent created")

    # 4. Weather Information Agent
    weather_agent = LlmAgent(
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
        tools=[weather_tool],
    )

    print("✓ Weather Information Agent created")

    # 5. Recommendations Agent
    recommendations_agent = LlmAgent(
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
        tools=[recommendations_tool],
    )

    print("✓ Travel Recommendations Agent created")
    print()

    # Create the coordinator agent
    tour_planner = LlmAgent(
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

    print(f"✓ Tour Planner Coordinator created")
    print(f"✓ Total sub-agents: {len(tour_planner.sub_agents)}")
    print()

    # Create runtime with tour planner as root agent
    runtime = Runtime(root_agent=tour_planner)
    print("✓ Runtime initialized with tour planning system")

    # Create session service
    session_service = SessionService(runtime=runtime)
    print("✓ Session service created")

    # Create a new session
    session = session_service.create_session()
    print(f"✓ Session created: {session.id}")
    print()
    print("-" * 70)
    print()

    # Interactive conversation loop
    print("Welcome to the AI Tour Planner!")
    print("Ask me to help plan your next trip (type 'quit' or 'exit' to end)")
    print()
    print("Example requests:")
    print("  - 'Plan a 5-day trip to Paris for 2 people'")
    print("  - 'I want to visit Tokyo for a week with a $4000 budget'")
    print("  - 'Create an itinerary for Rome focusing on history and food'")
    print()

    while True:
        # Get user input
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nHappy travels! Goodbye!")
            break

        # Send message and get response
        try:
            response = session_service.send(
                session_id=session.id,
                message=user_input
            )

            # Display the response
            print(f"\nTour Planner: {response.content}\n")
            print("-" * 70)
            print()

        except Exception as e:
            print(f"\nError: {e}\n")
            continue


if __name__ == "__main__":
    main()
