"""
POC 03: LLMAgent with Groq + Custom Websearch Tool

This demonstrates creating a custom web search tool and integrating it with a Groq-powered agent.

To run this agent:
  adk run .               # Run in terminal
  adk web                 # Run in browser UI
  adk api_server          # Start API server
"""

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from tools import web_search

# Create LiteLLM wrapper for Groq
groq_model = LiteLlm(
    model="groq/llama-3-groq-70b-8192-tool-use-preview",
)

# Define the root agent with custom web search tool
root_agent = Agent(
    name="web_search_assistant",
    model=groq_model,
    description="An AI assistant that can search the web for current information",
    instruction="""You are a helpful AI assistant with access to web search.

    When users ask questions that require current information, recent news,
    or data you don't have, use the web_search tool to find relevant information.

    Always provide clear, accurate answers based on the search results.
    Cite sources when providing information from search results.""",
    tools=[web_search],
)
