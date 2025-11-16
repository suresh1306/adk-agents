"""
POC 01: Simple LLMAgent with Gemini LLM

This demonstrates a basic conversational agent using Google's Gemini model
with the Google Agent Development Kit (ADK).

To run this agent:
  adk run .               # Run in terminal
  adk web                 # Run in browser UI
  adk api_server          # Start API server
"""

from google.adk.agents import Agent

# Define the root agent (required by ADK)
root_agent = Agent(
    name="gemini_assistant",
    model="gemini-2.0-flash-exp",  # Using Gemini 2.0 Flash
    description="A helpful AI assistant powered by Gemini",
    instruction="""You are a helpful, friendly AI assistant.
    Provide clear, concise, and accurate responses to user queries.
    Be conversational and engaging.""",
)
