# Google ADK Patterns - Based on Your POC Examples

## Pattern 1: Simple Agent (POC-01 & POC-02)

### Basic Structure with Gemini
```python
from google.adk.agents import Agent

root_agent = Agent(
    name="gemini_assistant",
    model="gemini-2.0-flash-exp",  # Direct model string for Gemini
    description="A helpful AI assistant powered by Gemini",
    instruction="""You are a helpful, friendly AI assistant.
    Provide clear, concise, and accurate responses to user queries.
    Be conversational and engaging.""",
)
```

### Basic Structure with Third-Party Provider (Groq)
```python
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

# Create LiteLLM wrapper for Groq
groq_model = LiteLlm(
    model="groq/llama-3.3-70b-versatile",  # Format: provider/model-name
)

# Use the wrapped model in agent
root_agent = Agent(
    name="groq_assistant",
    model=groq_model,  # Pass LiteLlm instance, not string
    description="A helpful AI assistant powered by Groq's Llama model",
    instruction="""You are a helpful, friendly AI assistant.
    Provide clear, concise, and accurate responses to user queries.
    Be conversational and engaging.""",
)
```

**Key Point**: Root agent MUST be defined at module level as `root_agent`

---

## Pattern 2: Agent with Custom Tools (POC-03 & POC-04)

### Tool Definition
```python
from typing import Dict, List, Union

# Simple tool returning dict
def web_search(query: str, max_results: int = 5) -> Dict[str, List[Dict[str, str]]]:
    """
    Search the web for information using DuckDuckGo.
    
    Use this tool when you need to find current information, recent news,
    or any data that requires searching the internet.
    
    Args:
        query: The search query string
        max_results: Maximum number of search results to return
    
    Returns:
        A dictionary containing search results with title, URL, and snippet
    """
    try:
        from duckduckgo_search import DDGS
        ddgs = DDGS()
        results = ddgs.text(query, max_results=max_results)
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "snippet": result.get("body", "")
            })
        
        return {
            "query": query,
            "results": formatted_results
        }
    
    except Exception as e:
        return {
            "query": query,
            "error": f"Search failed: {str(e)}",
            "results": []
        }


# Calculator tool
def calculate(expression: str) -> Dict[str, Union[str, float]]:
    """
    Evaluate a mathematical expression safely.
    
    Use this tool to perform calculations like addition, subtraction,
    multiplication, division, exponents, and basic functions.
    
    Args:
        expression: A mathematical expression as a string (e.g., "2 + 2", "sqrt(16)")
    
    Returns:
        A dictionary with the result
    """
    try:
        import math
        safe_dict = {
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log10,
            "ln": math.log,
            "pi": math.pi,
            "e": math.e,
        }
        
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        
        return {
            "expression": expression,
            "result": float(result),
            "success": True
        }
    
    except Exception as e:
        return {
            "expression": expression,
            "error": f"Calculation error: {str(e)}",
            "success": False
        }
```

### Agent with Tools
```python
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from tools import web_search, calculate

groq_model = LiteLlm(model="groq/llama-3.3-70b-versatile")

# Define agent with tools
root_agent = Agent(
    name="calculator_assistant",
    model=groq_model,
    description="A helpful AI assistant with web search and calculator capabilities",
    instruction="""You are a helpful assistant with access to web search and calculator tools.
    
    When users ask you to:
    - Find information: Use the web_search tool
    - Perform calculations: Use the calculate tool
    
    Always provide clear explanations of your findings.""",
    tools=[web_search, calculate]  # Pass functions directly
)
```

**Key Points**:
- Tools are regular Python functions
- Return dictionaries, not objects
- Include `success` field in response
- Pass raw functions to `tools=[]`, not strings
- Good docstrings help the LLM understand when to use tools

---

## Pattern 3: Multi-Agent System with Coordinator (POC-05 & POC-06)

### Create Specialized Sub-Agents
```python
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from tools import web_search, calculate, format_text

# Shared model
groq_model = LiteLlm(model="groq/llama-3.3-70b-versatile")

# 1. Research Agent
research_agent = Agent(
    name="research_agent",
    model=groq_model,
    description="Specializes in researching information and finding data online",
    instruction="""You are a research specialist. Your job is to:
    - Search the web for accurate, current information
    - Gather relevant facts and data
    - Provide well-sourced answers
    
    Use the web_search tool to find information when needed.""",
    tools=[web_search],
)

# 2. Math Agent
math_agent = Agent(
    name="math_agent",
    model=groq_model,
    description="Specializes in mathematical calculations and problem-solving",
    instruction="""You are a mathematics specialist. Your job is to:
    - Solve mathematical problems accurately
    - Perform calculations using the calculator tool
    - Explain mathematical concepts clearly
    
    Use the calculate tool for all computations.""",
    tools=[calculate],
)

# 3. Writer Agent
writer_agent = Agent(
    name="writer_agent",
    model=groq_model,
    description="Specializes in writing and content creation",
    instruction="""You are a writing specialist. Your job is to:
    - Create well-written content
    - Format text appropriately
    - Write in various styles
    
    Use the format_text tool when specific formatting is needed.""",
    tools=[format_text],
)
```

### Create Coordinator Agent with Sub-Agents
```python
# Root coordinator agent
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
    sub_agents=[research_agent, math_agent, writer_agent],  # Pass agent instances
)
```

**Key Points**:
- Sub-agents are created with specific roles and instructions
- Each sub-agent can have its own set of tools
- Coordinator delegates tasks intelligently
- Sub-agents can have specialized instructions

---

## Pattern 4: Tool Output Formats (From All POCs)

### Successful Tool Response
```python
def tool_success_example() -> dict:
    return {
        "status": "success",
        "result": "The actual result",
        "data": {"key": "value"},
        "metadata": "Additional info"
    }
```

### Error Tool Response
```python
def tool_error_example() -> dict:
    return {
        "status": "error",
        "error": "Description of what went wrong",
        "code": "ERROR_CODE",
        "success": False
    }
```

### Search Tool Response Pattern (POC-03, POC-05, POC-06)
```python
def search_tool(query: str) -> dict:
    try:
        # Processing...
        results = fetch_results(query)
        
        return {
            "query": query,
            "results": [
                {
                    "title": "Result Title",
                    "url": "https://example.com",
                    "snippet": "Result description"
                }
            ],
            "success": True
        }
    except Exception as e:
        return {
            "query": query,
            "error": f"Search failed: {str(e)}",
            "results": [],
            "success": False
        }
```

### Calculator Response Pattern (POC-04, POC-05)
```python
def calculate_result() -> dict:
    return {
        "expression": "2 + 2",
        "result": 4.0,
        "success": True
    }
```

### Itinerary/Complex Response Pattern (POC-06)
```python
def complex_output_example() -> dict:
    return {
        "destination": "Paris",
        "num_days": 5,
        "itinerary": [
            {
                "day": 1,
                "morning": "Morning activity",
                "afternoon": "Afternoon activity",
                "evening": "Evening activity"
            }
        ],
        "breakdown": {
            "accommodation": 500,
            "food": 250,
            "activities": 300
        },
        "total_cost": 1050,
        "success": True
    }
```

---

## Pattern 5: Tools with Context (Not in Current POCs, but Best Practice)

### Add ToolContext to Track Usage
```python
from google.adk.tools import ToolContext
from typing import Dict, Any

def web_search_with_context(
    query: str,
    max_results: int = 5,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    Search the web with session state tracking.
    ToolContext must be the last parameter.
    """
    try:
        from duckduckgo_search import DDGS
        
        # Track usage in state
        if tool_context:
            search_count = tool_context.state.get("tool:search_count", 0)
            tool_context.state["tool:search_count"] = search_count + 1
            tool_context.state["tool:last_search"] = query
        
        ddgs = DDGS()
        results = ddgs.text(query, max_results=max_results)
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "snippet": result.get("body", "")
            })
        
        return {
            "query": query,
            "results": formatted_results,
            "success": True
        }
    
    except Exception as e:
        return {
            "query": query,
            "error": str(e),
            "results": [],
            "success": False
        }
```

---

## Pattern 6: Running Agents

### Using ADK CLI (Recommended)
```bash
# Terminal interface (interactive chat)
cd poc-XX-name
adk run .

# Web UI
adk web

# API Server
adk api_server
```

### Direct Python (For Integration)
```python
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService

# Setup
session_service = DatabaseSessionService(db_url="sqlite:///./agent.db")
runner = Runner(root_agent=root_agent, session_service=session_service)

# Run agent with session
events = await runner.run(
    user_id="user123",
    session_id="session_123",
    new_message="User's question here"
)

# Process events
for event in events:
    if event.content:
        print(f"Agent: {event.content}")
```

---

## Execution Methods in Your POCs

Your POCs use the ADK CLI which:
1. Auto-detects `root_agent` at module level
2. Handles session management automatically
3. Provides multiple interfaces (terminal, web, API)
4. Manages conversation state transparently

**Running your POCs:**
```bash
cd poc-01-gemini-simple
adk run .                    # Terminal interface
# OR
adk web                      # Web UI at http://localhost:8000
# OR
adk api_server               # API at http://localhost:8000
```

---

## Summary: Key Takeaways from Your POCs

1. **Module-Level Root Agent**: All POCs define `root_agent` at module level
2. **Groq + LiteLlm**: POC-02+ use LiteLlm wrapper for Groq
3. **Tool Pattern**: Tools are functions returning dicts with `success` field
4. **Multi-Agent Pattern**: POC-05 & POC-06 show coordinator + specialists
5. **Shared Model**: Multiple agents can share same LiteLlm instance
6. **CLI Execution**: Use `adk run`, `adk web`, or `adk api_server` to run

Your POCs demonstrate the core patterns well but don't yet implement:
- Session persistence (InMemorySessionService is implicit)
- State management (no `output_key` or state modifications)
- Context objects (no CallbackContext or ToolContext)
- Structured outputs (no output_schema with Pydantic)

These features are available and documented above for future enhancement!
