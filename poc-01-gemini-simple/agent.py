#!/usr/bin/env python3
"""
POC 01: Simple LLMAgent with Gemini LLM

This demonstrates a basic conversational agent using Google's Gemini model
with the Google Agent Development Kit (ADK).
"""

import os
from google.adk.agents import LlmAgent
from google.adk.runners import Runtime
from google.adk.services import SessionService


def main():
    """Main function to run the Gemini agent."""

    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY environment variable not set")
        print("Please set it with: export GOOGLE_API_KEY='your-api-key'")
        return

    print("=" * 60)
    print("POC 01: Simple LLMAgent with Gemini")
    print("=" * 60)
    print()

    # Create the LLM Agent with Gemini
    agent = LlmAgent(
        name="gemini_assistant",
        model="gemini-2.0-flash-exp",  # Using Gemini 2.0 Flash
        description="A helpful AI assistant powered by Gemini",
        instruction="""You are a helpful, friendly AI assistant.
        Provide clear, concise, and accurate responses to user queries.
        Be conversational and engaging.""",
    )

    print(f"✓ Agent created: {agent.name}")
    print(f"✓ Model: {agent.model}")
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
    print("Chat with the Gemini assistant (type 'quit' or 'exit' to end)")
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
