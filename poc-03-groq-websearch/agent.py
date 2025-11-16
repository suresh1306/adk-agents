#!/usr/bin/env python3
"""
POC 03: LLMAgent with Groq + Custom Websearch Tool

This demonstrates creating a custom web search tool and using it with a Groq-powered agent.
"""

import os
from google.adk.agents import LlmAgent
from google.adk.runners import Runtime
from google.adk.services import SessionService
from google.adk.llms import LiteLlm
from google.adk.tools import FunctionTool
from tools import web_search


def main():
    """Main function to run the Groq agent with web search tool."""

    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY environment variable not set")
        print("Please set it with: export GROQ_API_KEY='your-api-key'")
        return

    print("=" * 60)
    print("POC 03: LLMAgent with Groq + Custom Websearch Tool")
    print("=" * 60)
    print()

    # Create LiteLLM wrapper for Groq
    groq_model = LiteLlm(
        model="groq/llama-3.3-70b-versatile",
    )

    print("✓ LiteLLM model configured for Groq")

    # Create the web search tool
    search_tool = FunctionTool(web_search)
    print("✓ Web search tool created")
    print()

    # Create the LLM Agent with Groq model and search tool
    agent = LlmAgent(
        name="web_search_assistant",
        model=groq_model,
        description="An AI assistant that can search the web for current information",
        instruction="""You are a helpful AI assistant with access to web search.

        When users ask questions that require current information, recent news,
        or data you don't have, use the web_search tool to find relevant information.

        Always provide clear, accurate answers based on the search results.
        Cite sources when providing information from search results.""",
        tools=[search_tool],
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
    print("Chat with the web search assistant (type 'quit' or 'exit' to end)")
    print("Try asking about current events or recent information!")
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
