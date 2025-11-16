#!/usr/bin/env python3
"""
POC 04: LLMAgent with Groq + Custom Calculator Tool

This demonstrates creating custom calculator tools and using them with a Groq-powered agent.
"""

import os
from google.adk.agents import LlmAgent
from google.adk.runners import Runtime
from google.adk.services import SessionService
from google.adk.llms import LiteLlm
from google.adk.tools import FunctionTool
from tools import calculate, advanced_math


def main():
    """Main function to run the Groq agent with calculator tools."""

    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY environment variable not set")
        print("Please set it with: export GROQ_API_KEY='your-api-key'")
        return

    print("=" * 60)
    print("POC 04: LLMAgent with Groq + Custom Calculator Tool")
    print("=" * 60)
    print()

    # Create LiteLLM wrapper for Groq
    groq_model = LiteLlm(
        model="groq/llama-3.3-70b-versatile",
    )

    print("✓ LiteLLM model configured for Groq")

    # Create calculator tools
    calc_tool = FunctionTool(calculate)
    advanced_math_tool = FunctionTool(advanced_math)

    print("✓ Calculator tools created")
    print("  - Basic calculator")
    print("  - Advanced math functions")
    print()

    # Create the LLM Agent with Groq model and calculator tools
    agent = LlmAgent(
        name="calculator_assistant",
        model=groq_model,
        description="An AI assistant that can perform mathematical calculations",
        instruction="""You are a helpful AI assistant with mathematical calculation capabilities.

        You have access to two tools:
        1. calculate() - For basic arithmetic and simple expressions
        2. advanced_math() - For trigonometric, logarithmic, and other advanced functions

        When users ask for calculations:
        - Use the appropriate tool based on the complexity
        - For angles in trig functions, assume degrees unless specified
        - Explain your calculations clearly
        - Show the steps when helpful""",
        tools=[calc_tool, advanced_math_tool],
    )

    print(f"✓ Agent created: {agent.name}")
    print(f"✓ Tools available: {len(agent.tools)}")
    print()

    # Create runtime for the agent
    runtime = Runtime(root_agent=agent)
    print("✓ Runtime initialized")

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
    print("Chat with the calculator assistant (type 'quit' or 'exit' to end)")
    print("Try asking math questions!")
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
