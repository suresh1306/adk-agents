"""
POC 06: Intelligent Tour Planner - Using Runner and InMemorySessionService

This demonstrates the Google ADK Runner pattern with explicit session management:
- google.adk.runners.Runner for orchestration
- google.adk.sessions.InMemorySessionService for state persistence
- google.adk.sessions.Session for session objects
- Full state management with temp: and user: scopes
- ToolContext integration in tools

To run this agent:
  python agent_runner.py

This is an async application that manages sessions explicitly using the Runner API.
"""

import asyncio
from datetime import datetime
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.genai.types import Content, Part
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

# Create LiteLLM wrapper for Groq with tool-use optimized model
groq_model = LiteLlm(model="groq/llama-3-groq-70b-8192-tool-use-preview")

# ============================================================================
# SPECIALIZED SUB-AGENTS WITH STATE MANAGEMENT
# ============================================================================

# 1. Destination Research Agent
research_agent = Agent(
    name="destination_researcher",
    model=groq_model,
    description="Researches destinations, attractions, and points of interest with context awareness",
    instruction=f"""You are a destination research specialist with access to web search and travel data.

**Your Expertise:**
- Finding information about tourist destinations worldwide
- Identifying popular attractions, hidden gems, and local experiences
- Researching local culture, customs, and etiquette
- Finding restaurants, accommodations, and transportation options

**CURRENT CONTEXT:**
- Today's date: {CURRENT_DATE}
- Current year: {CURRENT_YEAR}
- Provide current, up-to-date travel information relevant to {CURRENT_YEAR}
- Do NOT reference outdated COVID-19 pandemic restrictions from 2020-2022
- Focus on current visa requirements, travel policies, and safety guidelines

**SESSION STATE AWARENESS:**
You have access to conversation state. Use these values when available:
- {{{{temp:destination?}}}} - Currently researching destination (if already set)
- {{{{temp:travel_origin?}}}} - Traveler's starting location (if mentioned)
- {{{{temp:num_days?}}}} - Trip duration (if discussed)
- {{{{temp:num_people?}}}} - Number of travelers (if mentioned)

**Your Approach:**
1. Use search_destination tool to gather current information
2. Use calculate_travel_distance to provide travel logistics when origin is known
3. Reference state context to avoid asking for information already provided
4. Provide detailed, helpful insights with current, accurate information
5. Consider the traveler's context (origin, duration, group size) when making recommendations

Tools available: search_destination, calculate_travel_distance""",
    tools=[search_destination, calculate_travel_distance],
    output_key="research_summary"
)

# 2. Budget Calculator Agent
budget_agent = Agent(
    name="budget_calculator",
    model=groq_model,
    description="Calculates travel budgets with detailed breakdowns and cost-saving tips",
    instruction=f"""You are a budget planning specialist who helps travelers understand and optimize their trip expenses.

**SESSION STATE AWARENESS:**
Reference previous planning context when available:
- {{{{temp:destination?}}}} - Trip destination (if set)
- {{{{temp:num_days?}}}} - Number of days (if set)
- {{{{temp:num_people?}}}} - Number of travelers (if set)
- {{{{user:accommodation_preference?}}}} - User's preferred accommodation type (if previously mentioned)

**Your Approach:**
1. Use calculate_budget tool to generate detailed cost estimates
2. Reference destination and trip details from state when available
3. Provide realistic ranges and explain variations
4. Offer budget optimization suggestions
5. Account for seasonal price variations
6. Include contingency recommendations (typically 10-15%)

Tools available: calculate_budget""",
    tools=[calculate_budget],
    output_key="budget_plan"
)

# 3. Itinerary Builder Agent
itinerary_agent = Agent(
    name="itinerary_builder",
    model=groq_model,
    description="Creates personalized day-by-day travel itineraries",
    instruction=f"""You are an itinerary planning specialist who creates balanced, enjoyable travel schedules.

**SESSION STATE AWARENESS:**
Build upon existing planning context:
- {{{{temp:destination?}}}} - Trip destination
- {{{{temp:num_days?}}}} - Number of days to plan
- {{{{temp:interests?}}}} - Current trip interests (if specified)
- {{{{user:travel_interests?}}}} - User's general travel preferences (persists across trips!)
- {{{{temp:total_budget?}}}} - Total budget to stay within
- {{{{research_summary?}}}} - Previous destination research to reference

**Your Approach:**
1. Use create_itinerary tool to structure the schedule
2. Reference user's interests from state (current trip or general preferences)
3. Stay within budget constraints when known
4. Balance popular attractions with authentic local experiences
5. Include practical details: timing, logistics, backup options

Tools available: create_itinerary""",
    tools=[create_itinerary],
    output_key="itinerary_plan"
)

# 4. Weather Information Agent
weather_agent = Agent(
    name="weather_advisor",
    model=groq_model,
    description="Provides weather information and seasonal travel advice",
    instruction=f"""You are a weather and seasonal travel advisor helping travelers prepare for their trips.

**CURRENT CONTEXT:**
- Today's date: {CURRENT_DATE}
- Current season: Consider when providing advice

**SESSION STATE AWARENESS:**
Reference trip context when available:
- {{{{temp:destination?}}}} - Trip destination (if set)
- {{{{temp:num_days?}}}} - Trip duration for packing advice

**Your Approach:**
1. Use get_weather_info tool for seasonal data
2. Read destination from state if not explicitly provided
3. Provide month-specific or seasonal information
4. Suggest packing essentials based on conditions

Tools available: get_weather_info""",
    tools=[get_weather_info],
    output_key="weather_advice"
)

# 5. Travel Recommendations Agent
recommendations_agent = Agent(
    name="travel_advisor",
    model=groq_model,
    description="Provides personalized travel tips, recommendations, and advice",
    instruction=f"""You are a travel recommendations specialist sharing insider tips and cultural guidance.

**SESSION STATE AWARENESS:**
Personalize recommendations using context:
- {{{{temp:destination?}}}} - Trip destination
- {{{{user:travel_interests?}}}} - User's travel preferences (culture, food, adventure, etc.)
- {{{{temp:interests?}}}} - Current trip focus
- {{{{temp:num_days?}}}} - Trip duration affects recommendations

**Your Approach:**
1. Use get_travel_recommendations tool for curated tips
2. Read destination from state if not provided
3. Personalize based on user interests from state
4. Include both popular spots and hidden gems

Tools available: get_travel_recommendations""",
    tools=[get_travel_recommendations],
    output_key="travel_tips"
)

# ============================================================================
# COORDINATOR AGENT - INTELLIGENT TOUR PLANNER
# ============================================================================

coordinator_agent = Agent(
    name="intelligent_tour_planner",
    model=groq_model,
    description="Your personal AI travel planning assistant with memory and context awareness",
    instruction=f"""You are an Intelligent Tour Planning Assistant coordinating a team of travel specialists.

**YOUR TEAM:**
1. **Destination Researcher** - Finds attractions, activities, and destination information
2. **Budget Calculator** - Estimates costs and provides financial planning
3. **Itinerary Builder** - Creates day-by-day schedules
4. **Weather Advisor** - Provides seasonal information and packing advice
5. **Travel Advisor** - Shares tips, recommendations, and cultural guidance

**IMPORTANT CONTEXT:**
- Today's date: {CURRENT_DATE}
- Current year: {CURRENT_YEAR}
- Provide CURRENT information relevant to {CURRENT_YEAR}
- Do NOT mention COVID-19 pandemic restrictions (those ended in 2022-2023)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 SESSION STATE AWARENESS - YOUR MEMORY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Current Trip Planning State** (temp: scope - this trip only):
- {{{{temp:destination?}}}} - Destination being planned
- {{{{temp:num_days?}}}} - Number of days
- {{{{temp:num_people?}}}} - Number of travelers
- {{{{temp:travel_origin?}}}} - Traveler's starting location
- {{{{temp:total_budget?}}}} - Calculated total budget
- {{{{temp:interests?}}}} - Current trip interests/focus

**User Preferences** (user: scope - persists across ALL sessions):
- {{{{user:accommodation_preference?}}}} - Preferred accommodation type
- {{{{user:travel_interests?}}}} - General travel interests

**Previous Agent Work**:
- {{{{research_summary?}}}} - Latest destination research
- {{{{budget_plan?}}}} - Latest budget calculation
- {{{{itinerary_plan?}}}} - Latest itinerary
- {{{{weather_advice?}}}} - Latest weather info
- {{{{travel_tips?}}}} - Latest recommendations

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 INTELLIGENT CONVERSATION PRINCIPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**1. MEMORY & CONTEXT:**
- ✅ ALWAYS check state before asking questions
- ✅ Reference previous answers: "Based on the {{{{temp:destination?}}}} you mentioned..."
- ✅ Build upon previous work: "The budget we calculated earlier was {{{{temp:total_budget?}}}}..."
- ❌ NEVER ask for information already in state
- ❌ NEVER ignore previous conversation context

**2. COLLABORATIVE, NOT TRANSACTIONAL:**
- ✅ Engage in multi-turn conversations
- ✅ Ask clarifying questions to refine plans
- ✅ Offer suggestions and improvements
- ✅ Adapt based on feedback

**3. PROACTIVE ASSISTANCE:**
- Suggest next steps: "Would you like me to create a detailed itinerary?"
- Identify gaps: "I notice we haven't discussed accommodation yet..."
- Offer improvements: "Based on your culture interest, I'd recommend adding..."

**4. INTELLIGENT DELEGATION:**
- Coordinate with specialists based on user needs
- Pass context to sub-agents (they see the state too!)
- Synthesize their responses into coherent guidance

**Remember:** The state gives you memory. Use it to create a truly intelligent,
collaborative travel planning experience that feels personal and continuous!""",
    sub_agents=[
        research_agent,
        budget_agent,
        itinerary_agent,
        weather_agent,
        recommendations_agent
    ],
)


# ============================================================================
# RUNNER SETUP AND SESSION MANAGEMENT
# ============================================================================

async def main():
    """
    Main function demonstrating the Google ADK Runner pattern with session management.

    This shows how to:
    1. Create an InMemorySessionService
    2. Initialize a Runner with the agent and session service
    3. Create a session with initial state
    4. Process user messages using runner.run_async()
    5. Access session state across conversations
    """

    # Application and session identifiers
    APP_NAME = "TourPlannerApp"
    USER_ID = "user_001"  # In production, this would be the actual user ID
    SESSION_ID = "session_001"  # Can be generated per conversation

    print("=" * 80)
    print("🌍 Intelligent Tour Planner - Google ADK Runner Demo")
    print("=" * 80)
    print(f"\nApp: {APP_NAME}")
    print(f"User: {USER_ID}")
    print(f"Session: {SESSION_ID}")
    print(f"Date: {CURRENT_DATE}\n")

    # Step 1: Create InMemorySessionService
    # This manages session state in memory (for production, use DatabaseSessionService)
    session_service = InMemorySessionService()
    print("✅ Created InMemorySessionService\n")

    # Step 2: Create Runner with agent and session service
    # The Runner orchestrates the interaction flow between user, agent, and tools
    runner = Runner(
        agent=coordinator_agent,
        session_service=session_service,
        app_name=APP_NAME
    )
    print("✅ Created Runner with intelligent_tour_planner agent\n")

    # Step 3: Create a session with initial state
    # Sessions persist across multiple interactions
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state={}  # Start with empty state; tools and agents will populate it
    )
    print(f"✅ Created session: {session.id}\n")
    print("=" * 80)

    # Example conversation demonstrating state persistence
    conversation_examples = [
        "I want to plan a trip to Japan",
        "10 days, 2 people, we love food and culture",
        "What's the estimated budget?",
        "Can you create an itinerary?",
        "What's the weather like in Tokyo in spring?"
    ]

    print("\n📝 EXAMPLE CONVERSATION SIMULATION:")
    print("=" * 80)
    print("\nThis demonstrates how the agent maintains state across multiple turns.")
    print("After each interaction, you can see the session state being built up.\n")

    # Interactive mode
    print("💬 Starting Interactive Mode")
    print("=" * 80)
    print("Type your travel planning questions (or 'quit' to exit, 'state' to view state)\n")

    try:
        while True:
            # Get user input
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thank you for using Intelligent Tour Planner!")
                break

            if user_input.lower() == 'state':
                # Display current session state
                current_session = await session_service.get_session(
                    app_name=APP_NAME,
                    user_id=USER_ID,
                    session_id=SESSION_ID
                )
                print("\n📊 Current Session State:")
                print("-" * 80)
                if current_session and current_session.state:
                    for key, value in current_session.state.items():
                        print(f"  {key}: {value}")
                else:
                    print("  (empty)")
                print("-" * 80)
                print()
                continue

            # Create message content
            user_message = Content(
                role='user',
                parts=[Part(text=user_input)]
            )

            print("\nAgent: ", end="", flush=True)

            # Step 4: Run the agent with the user message
            # This processes the message, calls tools, manages state, and yields events
            agent_response = []
            async for event in runner.run_async(
                session_id=SESSION_ID,
                user_id=USER_ID,
                new_message=user_message
            ):
                # Process events from the agent
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts'):
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                agent_response.append(part.text)
                                print(part.text, end="", flush=True)

            print("\n")

            # Step 5: Optionally display updated state
            # Uncomment to see state changes after each turn:
            # current_session = await session_service.get_session(
            #     app_name=APP_NAME,
            #     user_id=USER_ID,
            #     session_id=SESSION_ID
            # )
            # print(f"\n[State updated: {len(current_session.state)} keys]")

    except KeyboardInterrupt:
        print("\n\n👋 Session interrupted. Goodbye!")

    finally:
        # Clean up
        print("\n" + "=" * 80)
        print("📊 FINAL SESSION STATE:")
        print("=" * 80)
        final_session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID
        )

        if final_session and final_session.state:
            print("\nSession stored the following information:")
            for key, value in final_session.state.items():
                # Truncate long values for display
                value_str = str(value)
                if len(value_str) > 100:
                    value_str = value_str[:100] + "..."
                print(f"  • {key}: {value_str}")
        else:
            print("\n  (No state was saved)")

        print("\n" + "=" * 80)
        print("✅ Session data persists in InMemorySessionService")
        print("   (Use DatabaseSessionService for production to persist across restarts)")
        print("=" * 80)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
