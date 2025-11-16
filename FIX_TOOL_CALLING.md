# Fix Summary: POC-03 Tool Calling Error

## Problem

POC-03 (and all Groq POCs) were failing with:
```
litellm.exceptions.BadRequestError: GroqException -
{"error":{"message":"Failed to call a function. Please adjust your prompt.",
"type":"invalid_request_error","code":"tool_use_failed"}}
```

## Root Cause

The `llama-3.3-70b-versatile` model has issues with function/tool calling in Groq's API.

## Solution

Changed all Groq POCs to use Groq's **dedicated tool-use model**:

```python
# ❌ Before (causes tool_use_failed error)
model="groq/llama-3.3-70b-versatile"

# ✅ After (optimized for tool calling)
model="groq/llama-3-groq-70b-8192-tool-use-preview"
```

## Why This Model?

According to Groq's documentation:
- `llama-3-groq-70b-8192-tool-use-preview` is **specifically designed for tool/function calling**
- It's the **highest performing model** on the Berkeley Function Calling Leaderboard (BFCL)
- Outperforms all other open source and proprietary models for tool use
- Built in collaboration with Glaive, optimized for structured output

## Affected POCs

All Groq-based POCs now use the correct model:

1. ✅ **POC-02**: groq-simple (basic agent, no tools - but updated for consistency)
2. ✅ **POC-03**: groq-websearch (web_search tool)
3. ✅ **POC-04**: groq-calculator (calculate, advanced_math tools)
4. ✅ **POC-05**: groq-subagents (multi-agent with tools)
5. ✅ **POC-06**: tour-planner (5 agents with 6 different tools)

## Testing

After merging, you can test POC-03:

```bash
git pull origin develop
cd poc-03-groq-websearch
export GROQ_API_KEY="your-groq-key"
adk run .
```

Then ask:
```
You: could you search about gold price and future prediction
```

The tool calling should now work without errors!

## Branch to Merge

**Feature Branch**: `claude/fix-groq-tool-use-01NGhHbyWhc2ZfYi8JgfnRGx`
**Target Branch**: `develop`
**Files Changed**: 5 (poc-02 through poc-06 agent.py files)
**Lines Changed**: 10 (5 lines changed, 2 per file)

## How to Merge

### Option 1: Via GitHub Pull Request
Visit: https://github.com/suresh1306/adk-agents/pull/new/claude/fix-groq-tool-use-01NGhHbyWhc2ZfYi8JgfnRGx

### Option 2: Command Line
```bash
git checkout develop
git pull origin develop
git merge origin/claude/fix-groq-tool-use-01NGhHbyWhc2ZfYi8JgfnRGx
git push origin develop
```

## Additional Notes

- The import fix (`from google.adk.models.lite_llm import LiteLlm`) was already in develop
- This branch **only changes the model** to fix tool calling
- No other functionality changed
- All POCs maintain the same interface and behavior
- The tool-use model is slightly slower but much more reliable for function calling
