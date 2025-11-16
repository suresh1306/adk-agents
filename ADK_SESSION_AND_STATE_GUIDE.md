# Google ADK Session Management, State, and Context Reference Guide

## 1. SESSION MANAGEMENT

### Overview
Session is the ADK object designed to track and manage individual conversation threads. Each session contains:
- **id**: Unique thread identifier
- **app_name**: Agent application name
- **user_id**: User identifier
- **events**: Chronological record of interactions
- **state**: Session state dictionary for temporary data
- **lastUpdateTime**: Timestamp of most recent event

### SessionService Implementations

#### InMemorySessionService
```python
from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()

# Create a session
session = await session_service.create_session(
    app_name="my_app",
    user_id="user123",
    state={"initial_key": "initial_value"}  # Optional
)

# Retrieve existing session
session = await session_service.get_session(
    app_name="my_app",
    user_id="user123",
    session_id="session_123"
)

# List sessions
sessions = await session_service.list_sessions(
    app_name="my_app"
)

# Delete session
await session_service.delete_session(session)
```

**Use Case**: Development, testing, quick prototyping
**Persistence**: None (lost on app restart)

#### DatabaseSessionService
```python
from google.adk.sessions import DatabaseSessionService

# SQLite example
session_service = DatabaseSessionService(
    db_url="sqlite:///./agent_data.db"
)

# PostgreSQL example
session_service = DatabaseSessionService(
    db_url="postgresql://user:password@localhost/dbname"
)

# MySQL example
session_service = DatabaseSessionService(
    db_url="mysql+pymysql://user:password@localhost/dbname"
)

# Same create/get/list/delete methods as InMemorySessionService
session = await session_service.create_session(
    app_name="my_app",
    user_id="user123"
)
```

**Use Case**: Self-managed persistent storage
**Persistence**: Yes, reliable across app restarts

#### VertexAiSessionService
```python
from google.adk.sessions import VertexAiSessionService
import os

session_service = VertexAiSessionService(
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location=os.environ["GOOGLE_CLOUD_LOCATION"],
    agent_engine_id=os.environ.get("AGENT_ENGINE_ID")
)

# Same methods as other session services
session = await session_service.create_session(
    app_name="my_app",
    user_id="user123"
)
```

**Use Case**: Production Google Cloud deployments with Vertex AI Agent Engine
**Persistence**: Yes, managed by Google Cloud

### Appending Events to Sessions
```python
from google.adk.sessions import Event, EventActions

# Create event with state changes
state_changes = {
    "task_status": "active",
    "user:login_count": 5,
    "temp:validation_needed": True
}

event = Event(
    invocation_id="inv_123",
    author="system",
    actions=EventActions(state_delta=state_changes)
)

# Append to session
await session_service.append_event(session, event)
```

---

## 2. STATE MANAGEMENT

### State Scope and Persistence

| Prefix | Scope | Persistence | Use Case |
|--------|-------|-------------|----------|
| None (default) | Current session only | Service-dependent | Task progress within current interaction |
| `user:` | All sessions for that user | Persistent services only | User preferences, profile data |
| `app:` | All users and sessions | Persistent services only | Global settings, shared templates |
| `temp:` | Current invocation only | Never persistent | Intermediate calculations, temporary flags |

### Example State Usage
```python
# Current session state (service-dependent persistence)
state["current_task"] = "processing"
state["step_count"] = 5

# User-level state (survives across different sessions for same user)
state["user:preferences"] = {"theme": "dark", "language": "en"}
state["user:subscription_level"] = "premium"

# Application-level state (shared across all users)
state["app:api_endpoint"] = "https://api.example.com/v2"
state["app:feature_flags"] = {"beta_search": True}

# Temporary state (lost after current invocation)
state["temp:validation_needed"] = True
state["temp:cache_key"] = "abc123"
```

### Reading State in Instructions
Use `{key}` templating to inject state values:

```python
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

model = LiteLlm(model="groq/llama-3.3-70b-versatile")

agent = Agent(
    name="story_generator",
    model=model,
    instruction="Write a story about {topic}. The user's favorite color is {user:favorite_color}.",
)
```

For optional keys, use `{key?}`:
```python
instruction="Write about {topic?}. Use this context if available: {user:context?}"
```

### Updating State: Three Approaches

#### 1. Using `output_key` (Simple)
Automatically saves agent response to state:
```python
from google.adk.agents import Agent

agent = Agent(
    name="greeter",
    model="gemini-2.0-flash-exp",
    instruction="Generate a friendly greeting.",
    output_key="last_greeting"  # Response saved to state["last_greeting"]
)
```

#### 2. Using `EventActions.state_delta` (Complex)
For multi-key updates:
```python
from google.adk.sessions import Event, EventActions

state_changes = {
    "current_status": "completed",
    "user:total_interactions": 10,
    "temp:needs_review": False
}

event = Event(
    invocation_id="inv_123",
    author="system",
    actions=EventActions(state_delta=state_changes)
)

await session_service.append_event(session, event)
```

#### 3. Using CallbackContext/ToolContext (Recommended)
Modify state within callbacks and tools:
```python
from google.adk.agents import CallbackContext
from google.adk.tools import ToolContext

# In a callback
def on_tool_end(context: CallbackContext, **kwargs):
    count = context.state.get("tool_calls", 0)
    context.state["tool_calls"] = count + 1
    # Changes automatically become part of event's state_delta

# In a tool function
def my_tool(tool_context: ToolContext, query: str) -> dict:
    # Read state
    user_pref = tool_context.state.get("user:display_preference", "default")
    api_endpoint = tool_context.state.get("app:api_endpoint")
    
    # Write state
    tool_context.state["tool:last_query"] = query
    tool_context.state["tool:calls_made"] = tool_context.state.get("tool:calls_made", 0) + 1
    
    return {"result": "processed"}
```

### Important: Avoid Direct State Modification
```python
# ❌ WRONG - Bypasses persistence, not thread-safe
session = await session_service.get_session(...)
session.state['key'] = value  # Direct modification

# ✅ CORRECT - Use append_event or context
event = Event(..., actions=EventActions(state_delta={'key': value}))
await session_service.append_event(session, event)
```

---

## 3. CONTEXT OBJECTS

### CallbackContext
Used in agent callbacks (pre/post-processing hooks):

```python
from google.adk.agents import CallbackContext

def my_agent_callback(context: CallbackContext, **kwargs):
    # Access agent info
    agent_name = context.agent.name
    
    # Read state
    task_status = context.state.get("task_status")
    
    # Write state
    context.state["callback_invoked"] = True
    context.state["user:interaction_count"] = context.state.get("user:interaction_count", 0) + 1
    
    # Access last tool result
    last_result = context.state.get("temp:last_api_result")
    
    return None
```

**Available Properties:**
- `context.agent` - Current agent object
- `context.state` - Session state dictionary
- `context.invocation_id` - Unique invocation ID

### ToolContext
Used in tool functions to access and modify session context:

```python
from google.adk.tools import ToolContext
from typing import Dict, Any

def my_tool(
    tool_context: ToolContext,
    param1: str,
    param2: int
) -> Dict[str, Any]:
    """Tool description for the LLM."""
    
    # Read state
    user_preference = tool_context.state.get("user:display_preference", "default")
    api_endpoint = tool_context.state.get("app:api_endpoint")
    
    # Process based on state
    if user_preference == "dark_mode":
        # Apply dark mode logic
        pass
    
    # Write state
    tool_context.state["tool:last_execution"] = "success"
    tool_context.state["tool:execution_count"] = tool_context.state.get("tool:execution_count", 0) + 1
    
    # Perform actual tool logic
    result = process_data(param1, param2)
    
    return {
        "status": "success",
        "result": result,
        "endpoint_used": api_endpoint
    }
```

**ToolContext Injection:**
ToolContext is automatically injected if it's the **last parameter** of your tool function.

---

## 4. AGENT CALLBACKS

Callbacks allow you to observe and customize agent behavior:

```python
from google.adk.agents import Agent, CallbackContext
from google.adk.models.lite_llm import LiteLlm

def on_agent_start(context: CallbackContext, **kwargs):
    print(f"Agent {context.agent.name} starting")
    context.state["temp:agent_start_time"] = time.time()

def on_agent_end(context: CallbackContext, **kwargs):
    start_time = context.state.get("temp:agent_start_time", 0)
    elapsed = time.time() - start_time
    context.state["agent:last_duration"] = elapsed
    print(f"Agent {context.agent.name} finished in {elapsed}s")

model = LiteLlm(model="groq/llama-3.3-70b-versatile")

agent = Agent(
    name="processor",
    model=model,
    description="Processes user requests",
    instruction="You are a helpful processor.",
    on_agent_start=on_agent_start,
    on_agent_end=on_agent_end
)
```

**Callback Types:**
- `on_agent_start` - Called when agent starts processing
- `on_agent_end` - Called when agent finishes
- `on_tool_start` - Called before tool execution
- `on_tool_end` - Called after tool execution
- `on_model_start` - Called before model invocation
- `on_model_end` - Called after model response

---

## 5. STRUCTURED OUTPUTS (output_key and output_schema)

### Using output_key (Simple)
Automatically saves agent response to session state:

```python
from google.adk.agents import Agent

summary_agent = Agent(
    name="summarizer",
    model="gemini-2.0-flash-exp",
    description="Summarizes text",
    instruction="Summarize the following text concisely.",
    output_key="last_summary"  # Saves response to state["last_summary"]
)
```

### Using output_schema (Structured)
Enforce structured JSON responses using Pydantic:

```python
from google.adk.agents import Agent
from pydantic import BaseModel, Field

class EmailContent(BaseModel):
    subject: str = Field(description="Email subject line")
    body: str = Field(description="Email body text")
    to_address: str = Field(description="Recipient email")

class CityInfo(BaseModel):
    city: str = Field(description="City name")
    country: str = Field(description="Country name")
    population: int = Field(description="Population")
    capital: bool = Field(description="Is this a capital city?")

# Email generation with structured output
email_agent = Agent(
    name="email_generator",
    model="gemini-2.0-flash-exp",
    description="Generates professional emails",
    instruction="Generate a professional email based on the user's request.",
    output_schema=EmailContent,
    output_key="generated_email"  # Saves structured response to state
)

# City information with structured output
city_agent = Agent(
    name="city_info",
    model="gemini-2.0-flash-exp",
    description="Provides city information",
    instruction="Provide information about the requested city in the specified format.",
    output_schema=CityInfo,
    output_key="city_data"
)
```

**Important Notes:**
- `output_schema` requires response to match Pydantic model structure
- `output_key` automatically saves the response to session state
- Use Pydantic `Field` with `description` for better LLM understanding
- Tools work with `output_schema` (limitation was lifted in recent versions)

---

## 6. TOOL CREATION AND CONTEXT

### Basic Tool Structure
```python
from google.adk.tools import ToolContext
from typing import Dict, Any

def web_search(
    query: str,
    max_results: int = 5,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    Search the web for information using DuckDuckGo.
    
    Args:
        query: The search query string
        max_results: Maximum number of results to return
        tool_context: Injected by ADK for state access
    
    Returns:
        Dictionary with search results
    """
    try:
        from duckduckgo_search import DDGS
        
        # Read from state if context available
        if tool_context:
            user_lang = tool_context.state.get("user:language", "en")
        
        # Perform search
        ddgs = DDGS()
        results = ddgs.text(query, max_results=max_results)
        
        # Update state
        if tool_context:
            tool_context.state["tool:last_search"] = query
            tool_context.state["tool:searches_count"] = tool_context.state.get("tool:searches_count", 0) + 1
        
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
            "success": False
        }

def calculate(
    expression: str,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    Evaluate a mathematical expression safely.
    
    ToolContext is optional but recommended for state tracking.
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
        
        if tool_context:
            tool_context.state["tool:calculations"] = tool_context.state.get("tool:calculations", 0) + 1
        
        return {
            "expression": expression,
            "result": float(result),
            "success": True
        }
    
    except Exception as e:
        return {
            "expression": expression,
            "error": str(e),
            "success": False
        }
```

---

## 7. COMPLETE AGENT EXAMPLE WITH SESSION

```python
from google.adk.agents import Agent, CallbackContext
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner
from pydantic import BaseModel, Field
from typing import Dict, Any

# Define output schema
class SearchResult(BaseModel):
    query: str = Field(description="Original search query")
    summary: str = Field(description="Summary of findings")
    top_sources: list = Field(description="List of top sources")

# Define tools with context
def web_search_tool(
    query: str,
    tool_context = None
) -> Dict[str, Any]:
    """Search the web for information."""
    if tool_context:
        tool_context.state["tool:last_search_query"] = query
        search_count = tool_context.state.get("tool:search_count", 0)
        tool_context.state["tool:search_count"] = search_count + 1
    
    # Actual implementation would use DuckDuckGo or similar
    return {
        "query": query,
        "results": [],
        "success": True
    }

# Define callbacks
def on_agent_start(context: CallbackContext, **kwargs):
    context.state["temp:agent_start"] = True
    context.state["user:session_interactions"] = context.state.get("user:session_interactions", 0) + 1

def on_agent_end(context: CallbackContext, **kwargs):
    context.state["temp:agent_end"] = True

# Initialize model
model = LiteLlm(model="groq/llama-3.3-70b-versatile")

# Initialize session service
session_service = DatabaseSessionService(db_url="sqlite:///./agent.db")

# Create agent with structured output
research_agent = Agent(
    name="research_agent",
    model=model,
    description="Research and summarize information",
    instruction="""You are a research specialist.
    Search for information about: {query}
    User preferences: {user:preferences?}
    Previous searches: {temp:recent_searches?}""",
    tools=[web_search_tool],
    output_schema=SearchResult,
    output_key="research_result",
    on_agent_start=on_agent_start,
    on_agent_end=on_agent_end
)

# Use the agent
async def run_agent_example():
    # Create session
    session = await session_service.create_session(
        app_name="research_app",
        user_id="user123",
        state={
            "query": "machine learning",
            "user:preferences": "academic sources",
            "temp:recent_searches": []
        }
    )
    
    # Create runner
    runner = Runner(
        root_agent=research_agent,
        session_service=session_service
    )
    
    # Run agent
    events = await runner.run(
        user_id="user123",
        session_id=session.id,
        new_message="Research the latest trends in machine learning"
    )
    
    # Process results
    for event in events:
        print(f"Event: {event}")
    
    # Check updated state
    updated_session = await session_service.get_session(
        app_name="research_app",
        user_id="user123",
        session_id=session.id
    )
    print(f"Updated state: {updated_session.state}")
```

---

## 8. IMPORT PATHS SUMMARY

```python
# Core Agent and Model
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

# Sessions
from google.adk.sessions import (
    InMemorySessionService,
    DatabaseSessionService,
    VertexAiSessionService,
    Session,
    Event,
    EventActions
)

# Context and Callbacks
from google.adk.agents import CallbackContext
from google.adk.tools import ToolContext

# Runner
from google.adk.runners import Runner

# Structured Output
from pydantic import BaseModel, Field
```

---

## 9. BEST PRACTICES

1. **State Organization**
   - Use prefixes (`user:`, `app:`, `temp:`) for scope clarity
   - Store only essential, dynamic data
   - Keep state minimal and serializable

2. **Session Management**
   - Use `DatabaseSessionService` or `VertexAiSessionService` for production
   - Always use `append_event()` for state updates, never modify directly
   - Clean up old sessions when appropriate

3. **Context Usage**
   - Always use `CallbackContext` or `ToolContext` for state modifications
   - Make `ToolContext` the last parameter in tool functions
   - Use state templating in instructions with `{key}` syntax

4. **Tools and Structured Output**
   - Tools should return dictionaries with `success` field
   - Use `output_schema` with Pydantic for structured responses
   - Use `output_key` to automatically save responses to state

5. **Error Handling**
   - Tools should return error information in their response dict
   - Don't raise exceptions; return `success: False` with error message
   - Always handle missing state keys with `.get()` and defaults
