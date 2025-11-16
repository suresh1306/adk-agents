#!/usr/bin/env python3
"""
POC 05: LLMAgent with Groq + Sub Agents

This demonstrates a multi-agent system with a coordinator and specialized sub-agents.
"""

import os
from google.adk.agents import LlmAgent
from google.adk.runners import Runtime
from google.adk.services import SessionService
from google.adk.llms import LiteLlm
from google.adk.tools import FunctionTool
from tools import web_search, calculate, format_text


def main():
    """Main function to run the multi-agent system."""

    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY environment variable not set")
        print("Please set it with: export GROQ_API_KEY='your-api-key'")
        return

    print("=" * 60)
    print("POC 05: Multi-Agent System with Groq")
    print("=" * 60)
    print()

    # Create LiteLLM wrapper for Groq
    groq_model = LiteLlm(model="groq/llama-3.3-70b-versatile")

    print("✓ LiteLLM model configured for Groq")
    print()

    # Create tools
    search_tool = FunctionTool(web_search)
    calc_tool = FunctionTool(calculate)
    format_tool = FunctionTool(format_text)

    # Create specialized sub-agents

    # 1. Research Agent - handles web searches and information gathering
    research_agent = LlmAgent(
        name="research_agent",
        model=groq_model,
        description="Specializes in researching information and finding data online",
        instruction="""You are a research specialist. Your job is to:
        - Search the web for accurate, current information
        - Gather relevant facts and data
        - Provide well-sourced answers
        - Summarize findings clearly

        Use the web_search tool to find information when needed.""",
        tools=[search_tool],
    )

    print("✓ Research Agent created")

    # 2. Math Agent - handles calculations and mathematical problems
    math_agent = LlmAgent(
        name="math_agent",
        model=groq_model,
        description="Specializes in mathematical calculations and problem-solving",
        instruction="""You are a mathematics specialist. Your job is to:
        - Solve mathematical problems accurately
        - Perform calculations using the calculator tool
        - Explain mathematical concepts clearly
        - Show step-by-step solutions

        Use the calculate tool for all computations.""",
        tools=[calc_tool],
    )

    print("✓ Math Agent created")

    # 3. Writer Agent - handles content creation and formatting
    writer_agent = LlmAgent(
        name="writer_agent",
        model=groq_model,
        description="Specializes in writing and content creation",
        instruction="""You are a writing specialist. Your job is to:
        - Create well-written content
        - Format text appropriately
        - Write in various styles (creative, technical, etc.)
        - Edit and improve text

        Use the format_text tool when specific formatting is needed.""",
        tools=[format_tool],
    )

    print("✓ Writer Agent created")
    print()

    # Create the coordinator agent with sub-agents
    coordinator = LlmAgent(
        name="coordinator",
        model=groq_model,
        description="Coordinates tasks among specialized agents",
        instruction="""You are a coordinator agent managing a team of specialists:

        1. Research Agent - for web searches and information gathering
        2. Math Agent - for calculations and mathematical problems
        3. Writer Agent - for content creation and writing tasks

        Your job is to:
        - Understand user requests
        - Delegate tasks to the appropriate specialist agent
        - Combine results from multiple agents when needed
        - Provide comprehensive answers to users

        Choose the right agent(s) based on the task requirements.""",
        sub_agents=[research_agent, math_agent, writer_agent],
    )

    print(f"✓ Coordinator Agent created")
    print(f"✓ Sub-agents: {len(coordinator.sub_agents)}")
    print()

    # Create runtime with coordinator as root agent
    runtime = Runtime(root_agent=coordinator)
    print("✓ Runtime initialized with multi-agent system")

    # Create session service
    session_service = SessionService(runtime=runtime)
    print("✓ Session service created")

    # Create a new session
    session = session_service.create_session()
    print(f"✓ Session created: {session.id}")
    print()
    print("-" * 60)
    print()

    # Interactive conversation loop
    print("Chat with the multi-agent system (type 'quit' or 'exit' to end)")
    print("The coordinator will delegate your tasks to specialized agents!")
    print()
    print("Example queries:")
    print("  - 'Search for recent AI developments'")
    print("  - 'Calculate 15% of 2500'")
    print("  - 'Write a haiku about coding'")
    print()

    while True:
        # Get user input
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break

        # Send message and get response
        try:
            response = session_service.send(
                session_id=session.id,
                message=user_input
            )

            # Display the response
            print(f"\nAssistant: {response.content}\n")

        except Exception as e:
            print(f"\nError: {e}\n")
            continue


if __name__ == "__main__":
    main()
