"""
POC 05: LLMAgent with Groq + Sub Agents

This demonstrates a multi-agent system with a coordinator agent and specialized sub-agents.

To run this agent:
  adk run .               # Run in terminal
  adk web                 # Run in browser UI
  adk api_server          # Start API server
"""

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from tools import web_search, calculate, format_text

# Create LiteLLM wrapper for Groq (shared by all agents)
groq_model = LiteLlm(model="groq/llama-3.3-70b-versatile")

# Create specialized sub-agents

# 1. Research Agent - handles web searches and information gathering
research_agent = Agent(
    name="research_agent",
    model=groq_model,
    description="Specializes in researching information and finding data online",
    instruction="""You are a research specialist. Your job is to:
    - Search the web for accurate, current information
    - Gather relevant facts and data
    - Provide well-sourced answers
    - Summarize findings clearly

    Use the web_search tool to find information when needed.""",
    tools=[web_search],
)

# 2. Math Agent - handles calculations and mathematical problems
math_agent = Agent(
    name="math_agent",
    model=groq_model,
    description="Specializes in mathematical calculations and problem-solving",
    instruction="""You are a mathematics specialist. Your job is to:
    - Solve mathematical problems accurately
    - Perform calculations using the calculator tool
    - Explain mathematical concepts clearly
    - Show step-by-step solutions

    Use the calculate tool for all computations.""",
    tools=[calculate],
)

# 3. Writer Agent - handles content creation and formatting
writer_agent = Agent(
    name="writer_agent",
    model=groq_model,
    description="Specializes in writing and content creation",
    instruction="""You are a writing specialist. Your job is to:
    - Create well-written content
    - Format text appropriately
    - Write in various styles (creative, technical, etc.)
    - Edit and improve text

    Use the format_text tool when specific formatting is needed.""",
    tools=[format_text],
)

# Create the coordinator agent with sub-agents
root_agent = Agent(
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
