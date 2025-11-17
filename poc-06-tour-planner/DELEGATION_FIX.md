# POC-06 Coordinator Delegation Fix

## Problem Description

The intelligent tour planner coordinator agent was **not properly delegating** to its specialist sub-agents. Instead of using the budget_calculator, itinerary_builder, and other specialists, it would say things like:

❌ **Before (Broken):**
```
User: "What's the budget for 2 adults, 2 kids?"
Agent: "I don't have access to budget_calculator information"
```

This caused two issues:
1. **The agent refused to help** instead of delegating to specialists
2. **Groq model errors** - The model tried to generate invalid output like `"For context:[budget_calculator]"` which caused `tool_use_failed` exceptions

## Root Cause

The coordinator agent's instructions were **too vague** about HOW to delegate to sub-agents. It didn't understand that:
- It's a COORDINATOR, not a direct executor
- It has NO tools itself
- It MUST delegate all specialized tasks to its team

## The Fix

I updated both `agent_complete.py` and `agent_runner.py` with **explicit delegation instructions**:

### 1. Clear Role Definition

Added at the top of coordinator instructions:
```
**CRITICAL: YOU MUST DELEGATE TO YOUR SPECIALIST TEAM**

You are a COORDINATOR, not a direct executor. You do NOT have tools yourself.
You MUST delegate all specialized tasks to your team of sub-agents.
```

### 2. Specialist Team Roster

Listed all 5 sub-agents with specific use cases:

```
1. **destination_researcher** - Use for:
   - Finding information about destinations
   - Researching attractions and points of interest
   - When user asks: "tell me about [destination]", "what to see in [place]"

2. **budget_calculator** - Use for:
   - Calculating travel budgets and costs
   - Budget breakdowns and estimates
   - When user asks: "what's the budget", "how much will it cost"

3. **itinerary_builder** - Use for:
   - Creating day-by-day travel itineraries
   - When user asks: "create itinerary", "plan my days"

4. **weather_advisor** - Use for:
   - Weather information and forecasts
   - When user asks: "what's the weather", "what to pack"

5. **travel_advisor** - Use for:
   - Travel tips and recommendations
   - When user asks: "any tips", "what should I know"
```

### 3. Concrete Examples

Added clear examples of CORRECT vs WRONG behavior:

✅ **CORRECT:**
```
User: "What's the budget for 2 people?"
You: "Let me consult our budget specialist to calculate that for you."
→ Then budget_calculator handles it
```

❌ **WRONG:**
```
User: "What's the budget?"
You: "I don't have access to budget_calculator" ← NEVER say this!
```

### 4. Workflow Example

Added a complete example showing natural delegation:

```
User: "I want to visit Jordan for 5 days"
You: "Wonderful! Let me gather information about Jordan for you."
→ destination_researcher provides research

You: "Jordan is amazing! Now, how many people are traveling?"
User: "2 adults, 2 kids, mid-range budget"

You: "Perfect! Let me calculate a budget for your family."
→ budget_calculator provides budget estimate

You: "Here's the estimated budget... Would you like me to create an itinerary?"
```

## Expected Behavior After Fix

### Budget Requests
```
User: "What's the budget for 2 adults and 2 kids for mid-range?"
Agent: "I'll calculate a mid-range budget for your family of 4. Let me work with our budget specialist."
→ Delegates to budget_calculator
→ budget_calculator uses calculate_budget tool
→ Returns detailed budget breakdown
Agent: "Here's the budget estimate..."
```

### Destination Research
```
User: "Tell me about Jordan"
Agent: "I'll gather information about Jordan for you."
→ Delegates to destination_researcher
→ destination_researcher uses search_destination tool
→ Returns destination information
Agent: "Jordan offers amazing experiences..."
```

### Itinerary Creation
```
User: "Create a 5-day itinerary"
Agent: "I'll create a personalized 5-day itinerary for Jordan."
→ Delegates to itinerary_builder
→ itinerary_builder uses create_itinerary tool
→ Returns day-by-day plan
Agent: "Here's your itinerary..."
```

## Testing the Fix

### Test Case 1: Budget Calculation
```bash
python agent_runner.py

You: I want to visit Jordan for 5 days
Agent: [Should delegate to destination_researcher]

You: could you prepare total budget for 2 adults and 2 kids for mid-range
Agent: [Should delegate to budget_calculator and provide budget breakdown]
```

**Expected:** Budget calculator is invoked, budget is calculated and presented

### Test Case 2: Multiple Delegations
```bash
You: Tell me about Tokyo
Agent: [Delegates to destination_researcher]

You: What's the weather like?
Agent: [Delegates to weather_advisor]

You: Create a 7-day itinerary
Agent: [Delegates to itinerary_builder]
```

**Expected:** Each specialist is properly invoked for their domain

### Test Case 3: State Awareness
```bash
You: I want to visit Paris for 10 days, 2 people
Agent: [Saves to state: temp:destination=Paris, temp:num_days=10, temp:num_people=2]

You: What's the budget?
Agent: [Uses state values, delegates to budget_calculator with context]
```

**Expected:** Doesn't ask for destination/days/people again - uses state!

## Files Updated

1. **poc-06-tour-planner/agent_complete.py** (for `adk run .`)
   - Updated coordinator (root_agent) with delegation instructions

2. **poc-06-tour-planner/agent_runner.py** (for `python agent_runner.py`)
   - Updated coordinator (coordinator_agent) with delegation instructions

## Key Improvements

| Before | After |
|--------|-------|
| "I don't have access to budget_calculator" | "Let me calculate that for you" → delegates |
| Refused to help with specialized tasks | Automatically delegates to right specialist |
| Vague delegation instructions | Explicit, example-driven delegation guide |
| No understanding of coordinator role | Clear: "You are a coordinator with NO tools" |
| Model tried to generate invalid syntax | Model correctly delegates to sub-agents |

## How Google ADK Sub-Agent Delegation Works

In Google ADK, when you define `sub_agents=[...]` on a coordinator agent:

1. **ADK automatically exposes sub-agents as "tools"** to the coordinator
2. The coordinator can invoke sub-agents by mentioning their role/task
3. Sub-agents receive the same session state (via state templating)
4. Sub-agents execute their tools and return results
5. Coordinator synthesizes results and presents to user

**The key:** The coordinator's LLM needs clear instructions on WHEN and HOW to delegate!

## Troubleshooting

### Issue: Still getting "I don't have access to X"

**Solution:** The model might be caching. Try:
1. Start a new session (new SESSION_ID)
2. Clear any cached prompts
3. Ensure you're using the updated files (check git status)

### Issue: tool_use_failed errors

**Cause:** Model trying to generate invalid function call syntax

**Solution:**
- Use tool-use optimized model: `groq/llama-3-groq-70b-8192-tool-use-preview`
- Check that GROQ_API_KEY is set correctly
- Ensure network connectivity to api.groq.com

### Issue: Sub-agent not using tools

**Cause:** Sub-agent instructions might be unclear

**Solution:** Each sub-agent has explicit tool instructions like:
```python
budget_agent = Agent(
    ...
    instruction="""...
    **Your Approach:**
    1. Use calculate_budget tool to generate detailed cost estimates
    ...""",
    tools=[calculate_budget],  # ← Tool is available
    output_key="budget_plan"   # ← Result saved to state
)
```

## Summary

The fix ensures that:
- ✅ Coordinator **always delegates** to specialists
- ✅ Coordinator **never refuses** with "I don't have access"
- ✅ Each specialist is invoked for their domain expertise
- ✅ State is shared across all agents for continuity
- ✅ Natural, collaborative conversation flow

**The tour planner now works as an intelligent coordinator orchestrating a team of travel specialists!** 🎯
