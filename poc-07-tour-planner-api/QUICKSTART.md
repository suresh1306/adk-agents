# POC-07 Quick Start Guide

Get the Tour Planner API running in 3 minutes!

## Prerequisites

- Python 3.10 or higher
- GROQ API key ([Get one free here](https://console.groq.com/keys))

## Step 1: Install Dependencies

```bash
cd poc-07-tour-planner-api
pip install -r requirements.txt
```

## Step 2: Set API Key

Create `.env` file:

```bash
echo "GROQ_API_KEY=your_actual_groq_api_key_here" > .env
```

Or copy the example:

```bash
cp .env.example .env
# Then edit .env and add your GROQ_API_KEY
```

## Step 3: Run the Server

```bash
uvicorn api_server:app --reload
```

You should see:
```
🚀 Starting Tour Planner API...
✅ InMemorySessionService initialized
✅ Runner initialized with intelligent_tour_planner agent
🌍 Tour Planner API is ready!
INFO:     Uvicorn running on http://127.0.0.1:8000
```

## Step 4: Test It!

### Option A: Interactive Python Client

```bash
python test_client.py --interactive
```

Then type messages like:
- "I want to visit Japan"
- "What's the budget for 2 people?"
- "Create a 7-day itinerary"

### Option B: Automated Test

```bash
python test_client.py
```

Runs a complete conversation automatically.

### Option C: Web Browser

Open `test_client.html` in your browser and start chatting!

### Option D: API Docs

Visit http://localhost:8000/docs

Try the `/api/chat/stream` endpoint with this request:

```json
{
  "message": "I want to plan a trip to Paris",
  "user_id": "test_user",
  "session_id": "test_session"
}
```

## Example cURL Commands

### Streaming Chat (SSE)

```bash
curl -N -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to visit Tokyo for 10 days",
    "user_id": "user_001"
  }'
```

### Non-Streaming Chat

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the budget for 2 adults?",
    "user_id": "user_001",
    "session_id": "my_session"
  }'
```

### Create Session

```bash
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001"
  }'
```

### Get Session State

```bash
curl "http://localhost:8000/api/sessions/my_session?user_id=user_001"
```

## What's Happening?

1. **Server starts** with InMemorySessionService (sessions stored in RAM)
2. **User sends message** → API creates/retrieves session
3. **Runner processes** → Delegates to sub-agents (research, budget, itinerary, weather, recommendations)
4. **Tools execute** → Search web, calculate budgets, create itineraries
5. **State persists** → Trip details saved in session (destination, days, people, budget, etc.)
6. **Events stream** → Real-time responses sent to client via SSE

## Troubleshooting

### Server won't start

```bash
# Check if port 8000 is in use
lsof -i :8000

# Use a different port
uvicorn api_server:app --reload --port 8080
```

### "GROQ_API_KEY not set"

Make sure `.env` file exists and contains:
```
GROQ_API_KEY=gsk_xxxx...
```

### Test client can't connect

- Ensure server is running on port 8000
- Check firewall settings
- Try http://127.0.0.1:8000 instead of localhost

### Streaming not working

- Use `curl -N` (no buffering)
- Ensure client supports Server-Sent Events
- Check CORS settings if using web client from different origin

## Next Steps

- ✅ Read full [README.md](README.md) for complete documentation
- ✅ Explore API docs at http://localhost:8000/docs
- ✅ Customize agent instructions in `agent.py`
- ✅ Add custom tools in `tools.py`
- ✅ Switch to DatabaseSessionService for production

## Production Deployment

For production, see [README.md](README.md#production-deployment) for:
- Database session persistence
- Gunicorn with multiple workers
- Docker deployment
- CORS configuration
- Environment variables

---

**Need help?** Check the main [README.md](README.md) or create an issue on GitHub!
