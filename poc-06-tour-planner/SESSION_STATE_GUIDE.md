# POC-06: ADK Session and State Management Guide

This POC demonstrates comprehensive use of Google ADK's session and state management features for building intelligent, context-aware travel planning agents.

## Overview

POC-06 implements a multi-agent tour planning system that fully leverages ADK's state management capabilities:

- **ToolContext** integration for stateful tools
- **State scopes** (temp:, user:, app:) for organized data
- **output_key** for automatic state persistence
- **State templating** ({key}) for context-aware instructions
- **DatabaseSessionService** support for persistent storage

## Architecture

### State Flow

```
User Input → Coordinator Agent
             ↓
             Delegates to Sub-Agents
             ↓
             Sub-Agents use Tools
             ↓
             Tools write to state via ToolContext
             ↓
             Agent responses saved via output_key
             ↓
             State persists across conversation
             ↓
             Next interactions reference previous state
```

### State Scopes Used

| Scope | Keys | Purpose | Persistence |
|-------|------|---------|-------------|
| `temp:` | destination, num_days, num_people, total_budget, interests, itinerary | Current trip planning data | Session only |
| `user:` | accommodation_preference, travel_interests | User preferences | Across sessions (with DB) |
| Default | research_summary, budget_plan, itinerary_plan, weather_advice, travel_tips | Agent outputs via output_key | Session only |

## Implementation Details

### 1. Tools with ToolContext

All tools accept `ToolContext` as the last parameter for state access:

```python
def calculate_budget(
    destination: str,
    num_days: int,
    num_people: int,
    accommodation_type: str = "mid-range",
    tool_context: ToolContext = None  # Automatically injected by ADK
) -> Dict:
    # Save to state
    if tool_context:
        tool_context.state["temp:destination"] = destination
        tool_context.state["temp:num_days"] = num_days
        tool_context.state["user:accommodation_preference"] = accommodation_type

    # ... tool logic ...

    return result
```

**Key points:**
- ToolContext is automatically injected when it's the last parameter
- Read state with `tool_context.state.get("key", default)`
- Write state with `tool_context.state["key"] = value`
- Changes are automatically persisted via EventActions.state_delta

### 2. Agents with output_key

Each sub-agent uses `output_key` to save its response to state:

```python
research_agent = Agent(
    name="destination_researcher",
    model=groq_model,
    description="Researches destinations",
    instruction="...",
    tools=[search_destination],
    output_key="research_summary"  # Saves response to state["research_summary"]
)
```

**Benefits:**
- Agent responses automatically saved to state
- Can be referenced in subsequent conversations
- Enables building upon previous work
- Avoids redundant API calls

### 3. State Templating in Instructions

Agents use `{key}` syntax to reference state in their instructions:

```python
instruction="""
You are a budget planner.

STATEFUL CONTEXT AWARENESS:
{temp:destination?} - Trip destination (if set)
{temp:num_days?} - Number of days (if set)
{user:accommodation_preference?} - User's preferred accommodation type (if set)

Reference previous context from state when available.
"""
```

**Key points:**
- `{key}` - Required key (error if missing)
- `{key?}` - Optional key (blank if missing)
- Values are injected before sending to LLM
- Enables agents to "remember" previous context

### 4. Session Service Configuration

By default, ADK CLI uses InMemorySessionService. For production, use DatabaseSessionService:

#### Option A: SQLite (Simple, Local)

```python
from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner

# Create session service with SQLite
session_service = DatabaseSessionService(
    db_url="sqlite:///./tour_planner_sessions.db"
)

# Create runner with session service
runner = Runner(
    agent=root_agent,
    session_service=session_service
)

# Run the agent
await runner.run_async(
    app_name="tour_planner",
    user_id="user123",
    user_prompt="I want to plan a trip to Japan"
)
```

#### Option B: PostgreSQL (Production)

```python
from google.adk.sessions import DatabaseSessionService

# Create session service with PostgreSQL
session_service = DatabaseSessionService(
    db_url="postgresql://user:password@localhost/tour_planner_db"
)
```

#### Option C: Using `adk run` with Custom Session Service

Create `run_with_db.py`:

```python
import asyncio
from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner
from agent import root_agent

async def main():
    # Create persistent session service
    session_service = DatabaseSessionService(
        db_url="sqlite:///./tour_planner_sessions.db"
    )

    # Create runner
    runner = Runner(
        agent=root_agent,
        session_service=session_service
    )

    # Run interactively
    print("Tour Planner Agent with Persistent Sessions")
    print("=" * 50)

    app_name = "tour_planner"
    user_id = input("Enter your user ID: ")
    session_id = input("Enter session ID (or press Enter for new session): ")

    if not session_id:
        session_id = None  # Will create new session

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            break

        async for event in runner.run_async(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            user_prompt=user_input
        ):
            if hasattr(event, 'content') and event.content:
                print(f"\n[{event.author}]: {event.content.text}")

        # Get session ID for next iteration
        if not session_id:
            sessions = await session_service.list_sessions(app_name=app_name)
            if sessions:
                session_id = sessions[0].id

if __name__ == "__main__":
    asyncio.run(main())
```

Run with: `python run_with_db.py`

## State Management Examples

### Example 1: First Conversation

```
User: I want to plan a trip to Japan

Agent (Coordinator):
→ Delegates to research_agent
→ research_agent calls search_destination("Japan")
→ Tool saves: state["temp:destination"] = "Japan"
→ research_agent response saved: state["research_summary"] = "..."

State after:
{
  "temp:destination": "Japan",
  "research_summary": "Japan offers amazing culture, food, and temples..."
}
```

### Example 2: Building on Previous Context

```
User: How much would it cost for 2 people for 10 days?

Agent (Coordinator):
→ Reads from state: {temp:destination?} = "Japan"
→ Delegates to budget_agent
→ budget_agent calls calculate_budget("Japan", 10, 2)
→ Tool saves:
   state["temp:num_days"] = 10
   state["temp:num_people"] = 2
   state["temp:total_budget"] = 6500
→ budget_agent response saved: state["budget_plan"] = "..."

State after:
{
  "temp:destination": "Japan",
  "temp:num_days": 10,
  "temp:num_people": 2,
  "temp:total_budget": 6500,
  "research_summary": "...",
  "budget_plan": "For a 10-day trip to Japan for 2 people..."
}
```

### Example 3: Referencing Multiple State Keys

```
User: Create an itinerary focusing on culture and food

Agent (Coordinator):
→ Reads from state:
   {temp:destination?} = "Japan"
   {temp:num_days?} = 10
   {temp:total_budget?} = 6500
→ Delegates to itinerary_agent
→ itinerary_agent calls create_itinerary("Japan", 10, ["culture", "food"])
→ Tool saves:
   state["temp:interests"] = ["culture", "food"]
   state["user:travel_interests"] = ["culture", "food"]  # Persists for future trips!
→ itinerary_agent response saved: state["itinerary_plan"] = "..."

State after:
{
  "temp:destination": "Japan",
  "temp:num_days": 10,
  "temp:num_people": 2,
  "temp:total_budget": 6500,
  "temp:interests": ["culture", "food"],
  "user:travel_interests": ["culture", "food"],  # ← Persists!
  "research_summary": "...",
  "budget_plan": "...",
  "itinerary_plan": "Day 1: Tokyo temples and ramen..."
}
```

### Example 4: Future Trip Using Saved Preferences

```
User: Now I want to plan a trip to Italy

Agent (Coordinator):
→ Reads from state:
   {user:travel_interests?} = ["culture", "food"]  # From previous trip!
→ Uses saved interests to personalize planning
→ "I see you enjoy culture and food. Italy is perfect for that!"
```

## Best Practices

### 1. State Organization

**DO:**
```python
# Use appropriate scopes
state["temp:destination"] = "Japan"          # Current trip only
state["user:travel_style"] = "luxury"        # User preference (persists)
state["app:currency_rates"] = {...}          # Global data (persists)
```

**DON'T:**
```python
# Don't mix scopes inappropriately
state["destination"] = "Japan"               # Unclear scope
state["user:current_trip"] = {...}           # User scope for temp data
```

### 2. Tool State Access

**DO:**
```python
def my_tool(param: str, tool_context: ToolContext = None) -> Dict:
    if tool_context:
        # Read with defaults
        pref = tool_context.state.get("user:preference", "default")

        # Write clearly
        tool_context.state["temp:last_action"] = "completed"

    return {"success": True}
```

**DON'T:**
```python
def my_tool(param: str, tool_context: ToolContext = None) -> Dict:
    # Don't assume state keys exist
    pref = tool_context.state["user:preference"]  # May raise KeyError!

    # Don't directly modify session
    # (state changes via tool_context are handled automatically)

    return {"success": True}
```

### 3. Agent Instructions

**DO:**
```python
instruction="""
You are a planner.

CONTEXT:
{temp:destination?} - Trip destination (if set)
{user:interests?} - User interests (if set)

Reference context when available, but handle missing values gracefully.
"""
```

**DON'T:**
```python
instruction="""
You are a planner for {temp:destination}.  # Error if not set!
User always likes {user:interests}.        # Assumes always present
"""
```

### 4. output_key Usage

**DO:**
```python
agent = Agent(
    name="researcher",
    model=model,
    output_key="research_result",  # Clear, descriptive name
    # ...
)
```

**DON'T:**
```python
agent = Agent(
    name="researcher",
    model=model,
    output_key="res",  # Too vague
    # ...
)
```

## Debugging State

### View Current State

When using `adk run .`, state is maintained automatically. To debug:

```python
# Add callback to coordinator
def on_agent_end(context: CallbackContext, **kwargs):
    print("\n=== CURRENT STATE ===")
    for key, value in context.state.items():
        print(f"{key}: {value}")
    print("=" * 40)

root_agent = Agent(
    # ...
    on_agent_end=on_agent_end
)
```

### Inspect Session Database

If using DatabaseSessionService with SQLite:

```bash
sqlite3 tour_planner_sessions.db

# List sessions
SELECT * FROM sessions;

# View session state
SELECT id, state FROM sessions WHERE app_name = 'tour_planner';

# View events
SELECT * FROM events WHERE session_id = 'your-session-id';
```

## Production Considerations

### 1. Use DatabaseSessionService

Replace InMemorySessionService with DatabaseSessionService for:
- Session persistence across restarts
- Multi-instance deployments
- User session history

### 2. Clean Up Old Sessions

```python
# Periodic cleanup
sessions = await session_service.list_sessions(app_name="tour_planner")
for session in sessions:
    if session_is_old(session):
        await session_service.delete_session(session)
```

### 3. Handle State Migration

When changing state structure:
```python
# Migration logic
if tool_context:
    # Old format
    old_budget = tool_context.state.get("budget")
    if old_budget and not tool_context.state.get("temp:total_budget"):
        tool_context.state["temp:total_budget"] = old_budget
```

### 4. Secure Sensitive Data

```python
# Don't store passwords or tokens in state
# Use environment variables or secret management instead
```

## Testing

### Unit Test Tools with Mock Context

```python
from unittest.mock import Mock
from tools import calculate_budget

def test_calculate_budget_saves_state():
    # Create mock context
    mock_context = Mock()
    mock_context.state = {}

    # Call tool
    result = calculate_budget(
        destination="Paris",
        num_days=5,
        num_people=2,
        tool_context=mock_context
    )

    # Assert state was saved
    assert mock_context.state["temp:destination"] == "Paris"
    assert mock_context.state["temp:num_days"] == 5
    assert result["success"] == True
```

### Integration Test with Real Session Service

```python
import asyncio
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from agent import root_agent

async def test_session_persistence():
    session_service = InMemorySessionService()
    runner = Runner(agent=root_agent, session_service=session_service)

    # First interaction
    events1 = []
    async for event in runner.run_async(
        app_name="test",
        user_id="test_user",
        user_prompt="Plan trip to Japan"
    ):
        events1.append(event)

    # Get session
    sessions = await session_service.list_sessions(app_name="test")
    session = sessions[0]

    # Check state
    assert "temp:destination" in session.state
    assert session.state["temp:destination"] == "Japan"

if __name__ == "__main__":
    asyncio.run(test_session_persistence())
```

## Summary

POC-06 demonstrates a production-ready implementation of ADK session and state management:

✅ **ToolContext** for stateful tools
✅ **State scopes** (temp:, user:, app:) for organization
✅ **output_key** for automatic response persistence
✅ **State templating** for context-aware instructions
✅ **DatabaseSessionService** support for production
✅ **Comprehensive state flow** across multi-agent system

This architecture enables:
- Intelligent, context-aware conversations
- No redundant questions or API calls
- User preference persistence across sessions
- Scalable, production-ready deployment

## Further Reading

- [ADK Session and State Guide](../ADK_SESSION_AND_STATE_GUIDE.md) - Complete reference
- [ADK Documentation](https://ai.google.dev/adk) - Official docs
- [POC Examples](../ADK_PATTERNS_FROM_POC.md) - Patterns from all POCs
