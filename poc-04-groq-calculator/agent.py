"""
POC 04: LLMAgent with Groq + Custom Calculator Tool

This demonstrates creating custom calculator tools and integrating them with a Groq-powered agent.

To run this agent:
  adk run .               # Run in terminal
  adk web                 # Run in browser UI
  adk api_server          # Start API server
"""

from google.adk.agents import Agent
from google.adk.llms import LiteLlm
from tools import calculate, advanced_math

# Create LiteLLM wrapper for Groq
groq_model = LiteLlm(
    model="groq/llama-3.3-70b-versatile",
)

# Define the root agent with calculator tools
root_agent = Agent(
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
    tools=[calculate, advanced_math],
)
