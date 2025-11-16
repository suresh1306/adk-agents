# Google ADK Runner Pattern Guide

This guide explains how to use the **Runner** pattern with **InMemorySessionService** and **Session** objects in Google ADK.

## Table of Contents

1. [Two Patterns for Running ADK Agents](#two-patterns-for-running-adk-agents)
2. [Runner Pattern Architecture](#runner-pattern-architecture)
3. [Complete Code Example](#complete-code-example)
4. [Session Management](#session-management)
5. [State Scopes and Persistence](#state-scopes-and-persistence)
6. [When to Use Each Pattern](#when-to-use-each-pattern)

---

## Two Patterns for Running ADK Agents

Google ADK provides two ways to run agents:

### Pattern 1: Module-Level `root_agent` (Declarative)

**File:** `agent.py` or `agent_complete.py`

```python
from google.adk.agents import Agent

root_agent = Agent(
    name="my_agent",
    model="gemini-2.0-flash-exp",
    instruction="You are a helpful assistant"
)
```

**Run with:**
```bash
adk run .       # Terminal chat
adk web         # Browser UI
adk api_server  # API server
```

**Characteristics:**
- ✅ Simple and declarative
- ✅ ADK CLI handles all session management automatically
- ✅ Great for quick prototyping and development
- ✅ Works with `adk web` for browser UI
- ❌ Less control over session lifecycle
- ❌ Can't customize session behavior easily

---

### Pattern 2: Runner with InMemorySessionService (Programmatic)

**File:** `agent_runner.py`

```python
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents import Agent

# Create agent
agent = Agent(name="my_agent", ...)

# Create session service
session_service = InMemorySessionService()

# Create runner
runner = Runner(
    agent=agent,
    session_service=session_service,
    app_name="MyApp"
)

# Create session and run
session = await session_service.create_session(...)
async for event in runner.run_async(...):
    # Process events
```

**Run with:**
```bash
python agent_runner.py  # Your custom script
```

**Characteristics:**
- ✅ Full control over session management
- ✅ Can integrate into existing applications (FastAPI, Flask, etc.)
- ✅ Can customize session lifecycle and storage
- ✅ Can switch session services (InMemory, Database, VertexAI)
- ✅ Better for production deployments
- ❌ More complex setup
- ❌ Need to handle async code
- ❌ Can't use `adk web` directly

---

## Runner Pattern Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Your Application                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                   Runner                              │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  │  │
│  │  │   Agent     │  │SessionService│  │   Events    │  │  │
│  │  │             │──│  (InMemory)  │──│   Stream    │  │  │
│  │  │ +sub_agents │  │              │  │             │  │  │
│  │  │ +tools      │  │   Session    │  │  Tool calls │  │  │
│  │  │ +output_key │  │   • state    │  │  Responses  │  │  │
│  │  └─────────────┘  │   • events   │  │  State Δ    │  │  │
│  │                   └──────────────┘  └─────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  User Input → Runner → Agent → Tools → State → Response    │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

1. **Runner**: Orchestrates the interaction flow
   - Routes messages to agents
   - Manages tool calls
   - Updates session state
   - Yields events for streaming responses

2. **SessionService**: Manages session persistence
   - **InMemorySessionService**: Stores in RAM (dev/testing)
   - **DatabaseSessionService**: Stores in database (production)
   - **VertexAiSessionService**: Google Cloud integration

3. **Session**: Represents a conversation session
   - `id`: Unique session identifier
   - `app_name`: Application name
   - `user_id`: User identifier
   - `state`: Dictionary for state storage
   - `events`: List of conversation events
   - `last_update_time`: Timestamp

---

## Complete Code Example

### Imports

```python
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.adk.models.lite_llm import LiteLlm
from google.genai.types import Content, Part
import asyncio
```

### Agent Definition

```python
# Create model (can use Gemini or LiteLLM)
model = LiteLlm(model="groq/llama-3-groq-70b-8192-tool-use-preview")

# Define agent with state awareness
agent = Agent(
    name="intelligent_assistant",
    model=model,
    description="An intelligent assistant with memory",
    instruction="""You are a helpful assistant.

    **SESSION STATE:**
    - {{user:name?}} - User's name (if provided)
    - {{temp:topic?}} - Current conversation topic

    Use the state to remember context across messages.""",
    tools=[...],  # Your tools
    output_key="assistant_response"  # Saves response to state
)
```

### Session Service Setup

```python
# Create session service
session_service = InMemorySessionService()

# Create runner
runner = Runner(
    agent=agent,
    session_service=session_service,
    app_name="MyApp"
)
```

### Session Management

```python
async def main():
    # Application identifiers
    APP_NAME = "MyApp"
    USER_ID = "user_123"
    SESSION_ID = "session_456"

    # Create session with initial state
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state={"temp:initialized": True}  # Optional initial state
    )

    # Process user message
    user_message = Content(
        role='user',
        parts=[Part(text="Hello, my name is Alice")]
    )

    # Run agent and collect events
    async for event in runner.run_async(
        session_id=SESSION_ID,
        user_id=USER_ID,
        new_message=user_message
    ):
        # Process events
        if hasattr(event, 'content') and event.content:
            for part in event.content.parts:
                if hasattr(part, 'text'):
                    print(part.text, end='', flush=True)

    # Retrieve updated session
    updated_session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    # Access state
    print(f"\nState: {updated_session.state}")
```

---

## Session Management

### Creating Sessions

```python
# Create a new session
session = await session_service.create_session(
    app_name="TravelApp",
    user_id="user_001",
    session_id="session_abc",  # Optional, will be generated if not provided
    state={"initialized": True}  # Optional initial state
)
```

### Retrieving Sessions

```python
# Get existing session
session = await session_service.get_session(
    app_name="TravelApp",
    user_id="user_001",
    session_id="session_abc"
)

# Access session properties
print(f"Session ID: {session.id}")
print(f"State: {session.state}")
print(f"Events: {len(session.events)}")
```

### Listing Sessions

```python
# List all sessions for a user
sessions = await session_service.list_sessions(
    app_name="TravelApp",
    user_id="user_001"
)

for session in sessions:
    print(f"Session: {session.id}, Last updated: {session.last_update_time}")
```

### Deleting Sessions

```python
# Delete a session
await session_service.delete_session(
    app_name="TravelApp",
    user_id="user_001",
    session_id="session_abc"
)
```

---

## State Scopes and Persistence

ADK supports different state scopes for organizing data:

### State Scopes

1. **`temp:` scope** - Session-specific (temporary)
   ```python
   state["temp:destination"] = "Japan"
   state["temp:num_days"] = 10
   ```
   - Persists only for the current session
   - Cleared when session ends
   - Use for: Current conversation context, temporary calculations

2. **`user:` scope** - User-specific (persistent)
   ```python
   state["user:name"] = "Alice"
   state["user:preferences"] = {"theme": "dark"}
   ```
   - Persists across all sessions for the same user
   - Requires `DatabaseSessionService` for true persistence
   - Use for: User preferences, profile data, cross-session context

3. **`app:` scope** - Application-wide (global)
   ```python
   state["app:version"] = "1.0"
   state["app:config"] = {...}
   ```
   - Shared across all users and sessions
   - Use for: Application-level configuration, shared resources

### State in InMemorySessionService

**Important:** `InMemorySessionService` only persists state **in RAM**:
- ✅ State persists across multiple `run_async()` calls in the same session
- ✅ Perfect for development and testing
- ❌ State is **lost when application restarts**
- ❌ Not suitable for production (use `DatabaseSessionService`)

### State in DatabaseSessionService

For production with true persistence:

```python
from google.adk.sessions import DatabaseSessionService

# Create database session service
session_service = DatabaseSessionService(
    connection_string="postgresql://user:pass@localhost/mydb"
)

# Now state persists across application restarts
session = await session_service.create_session(...)
```

---

## When to Use Each Pattern

### Use Module-Level `root_agent` (agent.py) When:

✅ **Quick prototyping and development**
- You want to get started quickly
- Testing agent behavior and instructions
- Iterating on agent design

✅ **Using ADK CLI features**
- Need the browser UI (`adk web`)
- Want simple terminal chat (`adk run .`)
- Using ADK API server (`adk api_server`)

✅ **Simple applications**
- Single-agent applications
- Don't need custom session management
- ADK's default behavior is sufficient

### Use Runner Pattern (agent_runner.py) When:

✅ **Production deployments**
- Integrating into existing applications
- Need custom session lifecycle management
- Want to use DatabaseSessionService for persistence

✅ **Advanced integrations**
- Building FastAPI/Flask endpoints
- Creating custom UIs
- Implementing multi-tenant systems

✅ **Complex workflows**
- Need to programmatically control sessions
- Want to implement custom event processing
- Need fine-grained control over state management

✅ **Testing and CI/CD**
- Automated testing of agent behavior
- Need to inspect session state
- Want to mock session services

---

## POC-06 Implementations

This POC includes both patterns:

### 1. `agent_complete.py` - Module-level pattern
```bash
adk run .       # Simple terminal chat
adk web         # Browser UI with session management
```

**Best for:**
- Quick testing and demonstration
- Using the ADK web interface
- Development and iteration

### 2. `agent_runner.py` - Runner pattern
```bash
python agent_runner.py  # Custom interactive application
```

**Best for:**
- Understanding Runner API
- Production integration examples
- Custom session management
- Programmatic control

---

## Example: Converting Between Patterns

### From Module-Level to Runner

**Before (agent.py):**
```python
from google.adk.agents import Agent

root_agent = Agent(name="my_agent", ...)
```

**After (agent_runner.py):**
```python
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
import asyncio

coordinator_agent = Agent(name="my_agent", ...)  # Rename from root_agent

async def main():
    session_service = InMemorySessionService()
    runner = Runner(
        agent=coordinator_agent,
        session_service=session_service,
        app_name="MyApp"
    )

    session = await session_service.create_session(...)
    # ... run logic

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Best Practices

### 1. Session ID Management
```python
import uuid

# Generate unique session IDs
session_id = str(uuid.uuid4())
```

### 2. Error Handling
```python
try:
    session = await session_service.get_session(...)
    if session is None:
        session = await session_service.create_session(...)
except Exception as e:
    print(f"Session error: {e}")
```

### 3. State Organization
```python
# Use prefixes for organization
state = {
    # Temporary session data
    "temp:current_task": "planning",
    "temp:destination": "Paris",

    # User preferences
    "user:theme": "dark",
    "user:language": "en",

    # Agent outputs
    "research_summary": "...",
    "budget_plan": "..."
}
```

### 4. Event Processing
```python
async for event in runner.run_async(...):
    # Different event types
    if hasattr(event, 'content'):
        # Agent response
        process_content(event.content)
    elif hasattr(event, 'tool_call'):
        # Tool execution
        log_tool_call(event.tool_call)
```

---

## Resources

- **Official Documentation**: https://google.github.io/adk-docs/
- **Python API Reference**: https://google.github.io/adk-docs/api-reference/python/
- **Session Documentation**: https://google.github.io/adk-docs/sessions/session/
- **GitHub Repository**: https://github.com/google/adk-python
- **Examples**: https://github.com/google/adk-samples

---

## Summary

The **Runner pattern** provides programmatic control over ADK agents with explicit session management:

```python
InMemorySessionService() → Runner(agent, session_service) → run_async() → Events
```

Key benefits:
- Full control over session lifecycle
- Integration into existing applications
- Switchable session storage (InMemory → Database → VertexAI)
- Production-ready architecture

For POC-06, both implementations are provided:
- **agent_complete.py** - Simple, declarative (`adk run .`)
- **agent_runner.py** - Advanced, programmatic (`python agent_runner.py`)

Choose the pattern that best fits your use case! 🚀
