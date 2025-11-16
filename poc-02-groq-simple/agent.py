"""
POC 02: Simple LLMAgent with Groq Provider

This demonstrates using a third-party LLM provider (Groq) with Google ADK via LiteLLM.

To run this agent:
  adk run .               # Run in terminal
  adk web                 # Run in browser UI
  adk api_server          # Start API server
"""

from google.adk.agents import Agent
from google.adk.llms import LiteLlm

# Create LiteLLM wrapper for Groq
groq_model = LiteLlm(
    model="groq/llama-3.3-70b-versatile",  # Groq's Llama 3.3 70B model
)

# Define the root agent (required by ADK)
root_agent = Agent(
    name="groq_assistant",
    model=groq_model,
    description="A helpful AI assistant powered by Groq's Llama model",
    instruction="""You are a helpful, friendly AI assistant.
    Provide clear, concise, and accurate responses to user queries.
    Be conversational and engaging.""",
)
