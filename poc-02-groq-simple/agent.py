#!/usr/bin/env python3
"""
POC 02: Simple LLMAgent with Groq Provider

This demonstrates using Groq LLM provider with Google ADK via LiteLLM.
"""

import os
from google.adk.agents import LlmAgent
from google.adk.runners import Runtime
from google.adk.services import SessionService
from google.adk.llms import LiteLlm


def main():
    """Main function to run the Groq-powered agent."""

    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY environment variable not set")
        print("Please set it with: export GROQ_API_KEY='your-api-key'")
        return

    print("=" * 60)
    print("POC 02: Simple LLMAgent with Groq Provider")
    print("=" * 60)
    print()

    # Create LiteLLM wrapper for Groq
    groq_model = LiteLlm(
        model="groq/llama-3.3-70b-versatile",  # Groq's Llama 3.3 70B model
    )

    print("✓ LiteLLM model configured for Groq")
    print(f"✓ Model: llama-3.3-70b-versatile")
    print()

    # Create the LLM Agent with Groq model
    agent = LlmAgent(
        name="groq_assistant",
        model=groq_model,
        description="A helpful AI assistant powered by Groq's Llama model",
        instruction="""You are a helpful, friendly AI assistant.
        Provide clear, concise, and accurate responses to user queries.
        Be conversational and engaging.""",
    )

    print(f"✓ Agent created: {agent.name}")
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
    print("Chat with the Groq assistant (type 'quit' or 'exit' to end)")
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
