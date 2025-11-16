# Google ADK: Comprehensive Session, State, and Context Reference

This document provides a complete summary of what you found in the ADK codebase for session management, state persistence, and context handling.

## Quick Reference: Key Classes and Import Paths

### Session Management Classes
```python
from google.adk.sessions import (
    InMemorySessionService,        # In-memory storage (no persistence)
    DatabaseSessionService,         # Database storage (SQLite, PostgreSQL, MySQL)
    VertexAiSessionService,        # Google Cloud storage
    Session,                         # Session object
    Event,                           # Event in session history
    EventActions,                    # Actions for events (state_delta)
)
```

### Context Objects
```python
from google.adk.agents import CallbackContext       # For callbacks
from google.adk.tools import ToolContext            # For tools
```

### Runner and Core Classes
```python
from google.adk.agents import Agent, CallbackContext
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
```

### Structured Output
```python
from pydantic import BaseModel, Field
```

---

## 1. SESSION MANAGEMENT - Complete Reference

### What is a Session?
- Individual conversation thread
- Contains: id, app_name, user_id, events (history), state, lastUpdateTime
- Managed by SessionService
- Can persist across app restarts (depending on service type)

### SessionService Implementations

#### InMemorySessionService
**Best for**: Development, testing, quick prototyping
**Persistence**: None (lost on app restart)
**Setup**: No additional configuration

```python
from google.adk.sessions import InMemorySessionService

service = InMemorySessionService()
session = await service.create_session(app_name="app", user_id="user1")
```

#### DatabaseSessionService
**Best for**: Self-managed persistent storage
**Persistence**: Yes, across app restarts
**Supported databases**: SQLite, PostgreSQL, MySQL

```python
from google.adk.sessions import DatabaseSessionService

# SQLite
service = DatabaseSessionService(db_url="sqlite:///./agent.db")

# PostgreSQL
service = DatabaseSessionService(db_url="postgresql://user:pass@host/db")

# MySQL
service = DatabaseSessionService(db_url="mysql+pymysql://user:pass@host/db")

session = await service.create_session(app_name="app", user_id="user1")
```

#### VertexAiSessionService
**Best for**: Production Google Cloud deployments
**Persistence**: Yes, managed by Google Cloud
**Requirements**: GCP project, location, optional agent_engine_id

```python
from google.adk.sessions import VertexAiSessionService
import os

service = VertexAiSessionService(
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location=os.environ["GOOGLE_CLOUD_LOCATION"],
    agent_engine_id=os.environ.get("AGENT_ENGINE_ID")
)

session = await service.create_session(app_name="app", user_id="user1")
```

### SessionService Core Methods

```python
# Create new session
session = await service.create_session(
    app_name="my_app",
    user_id="user123",
    state={"initial_key": "value"}  # Optional initial state
)

# Get existing session
session = await service.get_session(
    app_name="my_app",
    user_id="user123",
    session_id="session_id"
)

# List sessions for app
sessions = await service.list_sessions(
    app_name="my_app",
    user_id="user123"  # Optional: filter by user
)

# Delete session
await service.delete_session(session)

# Append event (with state changes)
from google.adk.sessions import Event, EventActions

event = Event(
    invocation_id="inv_123",
    author="system",
    actions=EventActions(state_delta={"key": "new_value"})
)
await service.append_event(session, event)
```

---

## 2. STATE MANAGEMENT - Complete Reference

### What is State?
- Key-value dictionary for session data
- Persists across conversation turns (service-dependent)
- Accessible via context objects or state templating
- Serializable only (no custom objects)

### State Scopes

| Prefix | Scope | Persistence | Use Case |
|--------|-------|-------------|----------|
| None | Current session | Service-dependent | Current task data |
| user: | All user sessions | Persistent only | User preferences, profile |
| app: | All users/sessions | Persistent only | Global settings |
| temp: | Current invocation | Never | Temporary data |

### Reading State: Three Methods

#### 1. State Templating in Instructions
```python
agent = Agent(
    name="story_writer",
    model="gemini-2.0-flash-exp",
    instruction="""Write a story about {topic}.
    User's preference: {user:genre?}
    Previous stories: {app:story_count?}"""
)
```

The ADK automatically replaces `{key}` with state values before sending to LLM.
Use `{key?}` for optional keys.

#### 2. CallbackContext
```python
from google.adk.agents import CallbackContext

def on_agent_start(context: CallbackContext, **kwargs):
    topic = context.state.get("topic", "general")
    context.state["user:interactions"] = context.state.get("user:interactions", 0) + 1
```

#### 3. ToolContext
```python
from google.adk.tools import ToolContext

def my_tool(
    param: str,
    tool_context: ToolContext = None  # Must be last parameter
) -> dict:
    if tool_context:
        user_pref = tool_context.state.get("user:preference")
        tool_context.state["tool:last_call"] = param
    return {"result": "done"}
```

### Writing State: Three Approaches

#### 1. Using output_key (Simple)
```python
agent = Agent(
    name="summarizer",
    model="gemini-2.0-flash-exp",
    instruction="Summarize the text",
    output_key="summary"  # Auto-saves response to state["summary"]
)
```

#### 2. Using EventActions (Complex)
```python
from google.adk.sessions import Event, EventActions

state_updates = {
    "status": "complete",
    "user:count": 10,
    "temp:flag": True
}

event = Event(
    invocation_id="inv_123",
    author="system",
    actions=EventActions(state_delta=state_updates)
)

await session_service.append_event(session, event)
```

#### 3. Using Context Objects (Recommended)
```python
def on_tool_end(context: CallbackContext, **kwargs):
    context.state["calls"] = context.state.get("calls", 0) + 1
    # Changes automatically become part of event's state_delta
```

### Critical: Never Modify State Directly
```python
# ❌ WRONG - Bypasses persistence, not thread-safe
session = await service.get_session(...)
session.state['key'] = value  # NEVER DO THIS

# ✅ CORRECT - Use append_event or context objects
event = Event(..., actions=EventActions(state_delta={'key': value}))
await service.append_event(session, event)
```

---

## 3. CONTEXT OBJECTS - Complete Reference

### CallbackContext
**Where**: Agent callbacks (on_agent_start, on_agent_end, on_tool_start, on_tool_end)
**Purpose**: Observe and customize agent behavior

```python
from google.adk.agents import CallbackContext
import time

def on_agent_start(context: CallbackContext, **kwargs):
    context.state["temp:start_time"] = time.time()

def on_agent_end(context: CallbackContext, **kwargs):
    start = context.state.get("temp:start_time", 0)
    elapsed = time.time() - start
    context.state["agent:duration"] = elapsed

def on_tool_start(context: CallbackContext, **kwargs):
    context.state["temp:tool_start"] = time.time()

def on_tool_end(context: CallbackContext, **kwargs):
    context.state["tool:call_count"] = context.state.get("tool:call_count", 0) + 1
```

**Available Properties:**
- `context.agent` - Current agent object
- `context.state` - Session state dictionary
- `context.invocation_id` - Unique invocation ID

**Callback Types:**
- `on_agent_start` - Before agent processes
- `on_agent_end` - After agent completes
- `on_tool_start` - Before tool execution
- `on_tool_end` - After tool execution
- `on_model_start` - Before LLM call
- `on_model_end` - After LLM response

### ToolContext
**Where**: Tool function parameters
**Purpose**: Access and modify session state in tools

```python
from google.adk.tools import ToolContext
from typing import Dict, Any

def my_tool(
    query: str,
    max_results: int = 5,
    tool_context: ToolContext = None  # MUST be last parameter
) -> Dict[str, Any]:
    """Tool description here."""
    
    if tool_context:
        # Read state
        language = tool_context.state.get("user:language", "en")
        endpoint = tool_context.state.get("app:api_endpoint")
        
        # Write state
        tool_context.state["tool:last_query"] = query
        tool_context.state["tool:calls"] = tool_context.state.get("tool:calls", 0) + 1
    
    # Do actual work
    results = process(query, max_results)
    
    return {"query": query, "results": results, "success": True}
```

**Key Points:**
- ToolContext must be the LAST parameter
- ADK automatically injects it if present
- Optional - can use or ignore if not needed
- Automatically tracks state changes as state_delta

---

## 4. STRUCTURED OUTPUTS - Complete Reference

### output_key Parameter
Simple automatic saving of agent response to state

```python
agent = Agent(
    name="summarizer",
    model="gemini-2.0-flash-exp",
    description="Summarizes text",
    instruction="Provide a concise summary",
    output_key="text_summary"  # Response saved to state["text_summary"]
)
```

The agent's final response text is automatically saved to `state[output_key]`.

### output_schema Parameter
Enforce structured JSON responses using Pydantic models

```python
from google.adk.agents import Agent
from pydantic import BaseModel, Field

class EmailOutput(BaseModel):
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body text")
    to: str = Field(description="Recipient email")

class SummaryOutput(BaseModel):
    title: str = Field(description="Summary title")
    points: list = Field(description="Key points")
    length: str = Field(description="short/medium/long")

email_agent = Agent(
    name="email_writer",
    model="gemini-2.0-flash-exp",
    description="Writes professional emails",
    instruction="Generate a professional email matching the schema",
    output_schema=EmailOutput,
    output_key="generated_email"  # Saves structured response
)

summary_agent = Agent(
    name="summarizer",
    model="gemini-2.0-flash-exp",
    instruction="Summarize the document in the required format",
    output_schema=SummaryOutput,
    output_key="document_summary"
)
```

**Important:**
- `output_schema` enforces structure, fails if response doesn't match
- `output_key` saves response to state under given key
- Both can be used together
- Tools work with `output_schema` (recent feature)

---

## 5. AGENTS - Complete Reference

### Basic Agent Creation
```python
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

# For Gemini (direct string)
agent1 = Agent(
    name="gemini_agent",
    model="gemini-2.0-flash-exp",
    description="Does something",
    instruction="Behave like this"
)

# For other providers via LiteLlm
model = LiteLlm(model="groq/llama-3.3-70b-versatile")
agent2 = Agent(
    name="groq_agent",
    model=model,
    description="Does something",
    instruction="Behave like this"
)
```

### Agent with Tools
```python
def search_tool(query: str) -> dict:
    """Search documentation."""
    return {"results": [], "success": True}

def calculate_tool(expression: str) -> dict:
    """Calculate expression."""
    return {"result": 0, "success": True}

agent = Agent(
    name="tool_agent",
    model="gemini-2.0-flash-exp",
    description="Uses tools",
    instruction="Use tools to help users",
    tools=[search_tool, calculate_tool]  # Pass functions directly
)
```

### Agent with Callbacks
```python
def on_start(context: CallbackContext, **kwargs):
    context.state["started"] = True

def on_end(context: CallbackContext, **kwargs):
    context.state["finished"] = True

agent = Agent(
    name="callback_agent",
    model="gemini-2.0-flash-exp",
    description="Has callbacks",
    instruction="Process requests",
    on_agent_start=on_start,
    on_agent_end=on_end
)
```

### Agent with Sub-Agents (Multi-Agent)
```python
research_agent = Agent(
    name="researcher",
    model=model,
    description="Researches",
    instruction="Find information",
    tools=[search_tool]
)

writer_agent = Agent(
    name="writer",
    model=model,
    description="Writes",
    instruction="Create content",
    tools=[format_tool]
)

coordinator = Agent(
    name="coordinator",
    model=model,
    description="Coordinates",
    instruction="Delegate to specialists",
    sub_agents=[research_agent, writer_agent]
)
```

### Complete Agent Example
```python
from google.adk.agents import Agent, CallbackContext
from google.adk.models.lite_llm import LiteLlm
from pydantic import BaseModel, Field

class ResearchOutput(BaseModel):
    topic: str = Field(description="Research topic")
    summary: str = Field(description="Research summary")
    sources: list = Field(description="Source URLs")

def research_callback(context: CallbackContext, **kwargs):
    context.state["research:count"] = context.state.get("research:count", 0) + 1

model = LiteLlm(model="groq/llama-3.3-70b-versatile")

research_agent = Agent(
    name="research_agent",
    model=model,
    description="Researches topics",
    instruction="""Research: {research_topic}
    Focus: {user:research_focus?}
    Previous research: {app:previous_research_count?}""",
    tools=[search_tool],
    output_schema=ResearchOutput,
    output_key="research_result",
    on_agent_start=research_callback
)
```

---

## 6. TOOLS - Complete Reference

### Basic Tool Structure
```python
from typing import Dict, Any

def my_tool(param1: str, param2: int = 5) -> Dict[str, Any]:
    """
    Tool description - helps LLM understand when to use it.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter (default shown)
    
    Returns:
        Dictionary with results
    """
    try:
        # Do work
        result = process(param1, param2)
        
        return {
            "status": "success",
            "result": result,
            "param1": param1,
            "success": True
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "success": False
        }
```

### Tool with State Context
```python
from google.adk.tools import ToolContext
from typing import Dict, Any

def tracked_tool(
    query: str,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """Tool that tracks usage in state."""
    try:
        # Track in state
        if tool_context:
            count = tool_context.state.get("tool:calls", 0)
            tool_context.state["tool:calls"] = count + 1
            tool_context.state["tool:last_query"] = query
            
            # Read configuration
            config = tool_context.state.get("app:config", {})
        
        # Do actual work
        result = process(query, config if tool_context else {})
        
        return {
            "query": query,
            "result": result,
            "success": True
        }
    except Exception as e:
        return {
            "query": query,
            "error": str(e),
            "success": False
        }
```

### Tool Return Patterns

**Success Pattern:**
```python
return {
    "status": "success",
    "result": "The actual result",
    "metadata": "Additional info",
    "success": True
}
```

**Error Pattern:**
```python
return {
    "status": "error",
    "error": "Error description",
    "code": "ERROR_CODE",
    "success": False
}
```

---

## 7. RUNNER - Complete Reference

### Creating and Running with Runner
```python
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService

# Setup session service
session_service = DatabaseSessionService(db_url="sqlite:///./agent.db")

# Create runner
runner = Runner(
    root_agent=root_agent,
    session_service=session_service
)

# Run agent with session
async def process_request(user_id, query):
    # Create or get session
    session = await session_service.create_session(
        app_name="my_app",
        user_id=user_id
    )
    
    # Run agent
    events = await runner.run(
        user_id=user_id,
        session_id=session.id,
        new_message=query
    )
    
    # Process results
    for event in events:
        if event.content:
            print(f"Response: {event.content}")
    
    # Check updated state
    updated = await session_service.get_session(
        app_name="my_app",
        user_id=user_id,
        session_id=session.id
    )
    print(f"State: {updated.state}")
```

---

## 8. ADK CLI - For Your POCs

All your POCs use ADK CLI which automatically handles:
- Session management
- State persistence
- Context injection
- Event handling

```bash
# Terminal interface (recommended for testing)
cd poc-XX-name
adk run .

# Web UI at http://localhost:8000
adk web

# API server at http://localhost:8000
adk api_server
```

The CLI auto-detects `root_agent` at module level and handles everything else.

---

## 9. BEST PRACTICES CHECKLIST

Session Management:
- [ ] Use DatabaseSessionService or VertexAiSessionService for production
- [ ] InMemorySessionService only for development/testing
- [ ] Always use append_event() for state updates
- [ ] Never modify session.state directly

State Management:
- [ ] Use prefixes (user:, app:, temp:) for organization
- [ ] Store only serializable types
- [ ] Use .get() with defaults for missing keys
- [ ] Keep state minimal

Context Usage:
- [ ] Use CallbackContext in callbacks
- [ ] Make ToolContext last parameter in tools
- [ ] Use state templating in instructions
- [ ] Track usage for analytics/debugging

Tools:
- [ ] Return dicts, not objects
- [ ] Include success field
- [ ] Handle errors gracefully
- [ ] Write good docstrings for LLM

Structured Output:
- [ ] Use output_key for simple text responses
- [ ] Use output_schema for structured JSON
- [ ] Define Pydantic models with Field descriptions
- [ ] Test output schema compliance

---

## Files Added to Your Repository

1. `/home/user/adk-agents/ADK_SESSION_AND_STATE_GUIDE.md` - Complete reference with code examples
2. `/home/user/adk-agents/ADK_PATTERNS_FROM_POC.md` - Patterns from your specific POCs
3. `/home/user/adk-agents/ADK_COMPREHENSIVE_SUMMARY.md` - This file

---

## Resources

- Google ADK Docs: https://google.github.io/adk-docs/
- Google ADK GitHub: https://github.com/google/adk-python
- LiteLLM Docs: https://docs.litellm.ai/
- Pydantic Docs: https://docs.pydantic.dev/

---

## Next Steps for Your POCs

Your current POCs demonstrate:
- Basic agent creation
- Tool creation and usage
- Multi-agent coordination

To enhance them with session/state features:

1. **Add Session Persistence**: Replace implicit InMemory with DatabaseSessionService
2. **Track State**: Use output_key and state tracking callbacks
3. **Add Context**: Use CallbackContext and ToolContext for monitoring
4. **Structured Output**: Add output_schema to agents that need it
5. **State Templating**: Use {key} in instructions for dynamic behavior

These features will make your agents more powerful, persistent, and production-ready!
