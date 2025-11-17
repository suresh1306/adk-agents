# POC-07: Tour Planner FastAPI with Streaming

FastAPI wrapper around the intelligent tour planner agent with streaming chat support using Server-Sent Events (SSE).

## Features

- ✅ **Streaming Chat API** - Real-time responses using Server-Sent Events (SSE)
- ✅ **Non-Streaming Chat API** - Traditional request/response for simpler clients
- ✅ **Session Management** - Create, list, get, and delete sessions
- ✅ **Google ADK Runner Pattern** - Full state management with InMemorySessionService
- ✅ **CORS Support** - Ready for frontend integration
- ✅ **OpenAPI Documentation** - Auto-generated at `/docs` and `/redoc`
- ✅ **Health Check** - Monitor API status

## Quick Start

### 1. Install Dependencies

```bash
cd poc-07-tour-planner-api
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create `.env` file:

```bash
# Required: Groq API key for LLM
GROQ_API_KEY=your_groq_api_key_here

# Optional: For Gemini models
# GOOGLE_API_KEY=your_google_api_key_here
```

### 3. Run the API Server

```bash
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

Or using Python directly:

```bash
python api_server.py
```

### 4. Access the API

- **API Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/health

## API Endpoints

### 🏥 Health Check

```bash
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-17T10:30:00",
  "app_name": "TourPlannerAPI",
  "session_service": "InMemorySessionService"
}
```

### 💬 Streaming Chat (SSE)

```bash
POST /api/chat/stream
Content-Type: application/json

{
  "message": "I want to visit Japan for 10 days",
  "user_id": "user_123",
  "session_id": "session_abc"
}
```

**Response (Server-Sent Events):**
```
data: {"type": "content", "text": "Wonderful!", "role": "assistant"}

data: {"type": "tool_call", "tool": "search_destination", "status": "executing"}

data: {"type": "content", "text": " Let me gather information about Japan."}

data: {"type": "done", "session_id": "session_abc"}
```

### 💬 Non-Streaming Chat

```bash
POST /api/chat
Content-Type: application/json

{
  "message": "What's the budget for 2 adults and 2 kids?",
  "user_id": "user_123",
  "session_id": "session_abc"
}
```

**Response:**
```json
{
  "response": "Let me calculate a budget for your family of 4...",
  "session_id": "session_abc",
  "user_id": "user_123"
}
```

### 📝 Session Management

#### Create Session

```bash
POST /api/sessions
Content-Type: application/json

{
  "user_id": "user_123",
  "initial_state": {
    "temp:language": "en"
  }
}
```

#### List Sessions

```bash
GET /api/sessions?user_id=user_123
```

#### Get Session Details

```bash
GET /api/sessions/session_abc?user_id=user_123
```

#### Delete Session

```bash
DELETE /api/sessions/session_abc?user_id=user_123
```

## Usage Examples

### Using cURL - Streaming Chat

```bash
curl -N -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to plan a trip to Jordan",
    "user_id": "user_001",
    "session_id": "my_session"
  }'
```

### Using Python - Streaming Client

```python
import requests
import json

url = "http://localhost:8000/api/chat/stream"
data = {
    "message": "I want to visit Paris for 7 days",
    "user_id": "user_001",
    "session_id": "session_001"
}

response = requests.post(url, json=data, stream=True)

for line in response.iter_lines():
    if line:
        # Remove 'data: ' prefix
        if line.startswith(b'data: '):
            event_data = json.loads(line[6:])

            if event_data['type'] == 'content':
                print(event_data['text'], end='', flush=True)
            elif event_data['type'] == 'tool_call':
                print(f"\n[Calling {event_data['tool']}...]")
            elif event_data['type'] == 'done':
                print(f"\n\n✅ Session: {event_data['session_id']}")
                break
```

### Using Python - Non-Streaming Client

```python
import requests

url = "http://localhost:8000/api/chat"
data = {
    "message": "What's the budget for 2 people visiting Tokyo?",
    "user_id": "user_001",
    "session_id": "session_001"
}

response = requests.post(url, json=data)
result = response.json()

print(f"Response: {result['response']}")
print(f"Session: {result['session_id']}")
```

### Using JavaScript/Fetch - Streaming

```javascript
const eventSource = new EventSource('http://localhost:8000/api/chat/stream');

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'content') {
    document.getElementById('chat').innerHTML += data.text;
  } else if (data.type === 'done') {
    console.log('Conversation complete');
    eventSource.close();
  }
};
```

## Test Client

A simple test client is provided:

```bash
python test_client.py
```

This will:
1. Create a new session
2. Send multiple chat messages
3. Display streaming responses
4. Show final session state

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              API Endpoints                            │  │
│  │  • POST /api/chat/stream   (SSE streaming)           │  │
│  │  • POST /api/chat          (non-streaming)           │  │
│  │  • POST /api/sessions      (create session)          │  │
│  │  • GET  /api/sessions      (list sessions)           │  │
│  └───────────────────────────────────────────────────────┘  │
│                           ↓                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                   Runner                              │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  │  │
│  │  │   Agent     │  │SessionService│  │   Events    │  │  │
│  │  │ coordinator │──│  (InMemory)  │──│   Stream    │  │  │
│  │  │ 5 sub-agents│  │              │  │             │  │  │
│  │  │ + tools     │  │   Session    │  │  Tool calls │  │  │
│  │  │ + state     │  │   • state    │  │  Responses  │  │  │
│  │  └─────────────┘  │   • events   │  │  State Δ    │  │  │
│  │                   └──────────────┘  └─────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓
                    SSE Event Stream
                           ↓
                      Client Browser
```

## Event Types

The streaming endpoint returns different event types:

### Content Event
```json
{
  "type": "content",
  "text": "Hello! I'm your tour planner...",
  "role": "assistant"
}
```

### Tool Call Event
```json
{
  "type": "tool_call",
  "tool": "search_destination",
  "status": "executing"
}
```

### Tool Result Event
```json
{
  "type": "tool_result",
  "tool": "search_destination",
  "status": "completed"
}
```

### Done Event
```json
{
  "type": "done",
  "session_id": "session_abc"
}
```

### Error Event
```json
{
  "type": "error",
  "message": "Error description",
  "error_type": "ValueError"
}
```

## State Management

The API uses Google ADK's session management:

**State Scopes:**
- `temp:destination` - Current trip destination (session only)
- `temp:num_days` - Trip duration (session only)
- `user:travel_interests` - User preferences (persistent across sessions)

**Agent Outputs** (automatically saved):
- `research_summary` - Destination research results
- `budget_plan` - Budget calculations
- `itinerary_plan` - Day-by-day itinerary

## Production Deployment

### Switch to Database Session Service

For production, replace `InMemorySessionService` with `DatabaseSessionService`:

```python
from google.adk.sessions import DatabaseSessionService

# In lifespan startup
session_service = DatabaseSessionService(
    connection_string="postgresql://user:pass@localhost/tourplanner"
)
```

### Environment Variables

```bash
# Database (for DatabaseSessionService)
DATABASE_URL=postgresql://user:pass@localhost/tourplanner

# API Keys
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key

# CORS (comma-separated)
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### Run with Gunicorn

```bash
gunicorn api_server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Troubleshooting

### Issue: Streaming not working

**Solution:** Ensure your client supports Server-Sent Events and doesn't buffer responses. Use `curl -N` or set appropriate headers.

### Issue: CORS errors

**Solution:** Update `allow_origins` in the CORS middleware:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    ...
)
```

### Issue: Session not persisting

**Solution:** InMemorySessionService stores sessions in RAM only. Use DatabaseSessionService for persistence across restarts.

## Testing

Run the test suite:

```bash
pytest test_api_server.py -v
```

## Related Files

- `agent.py` - Tour planner coordinator and sub-agents (from POC-06)
- `tools.py` - Travel planning tools with state management (from POC-06)
- `api_server.py` - FastAPI application with streaming
- `test_client.py` - Simple test client for streaming chat

## Resources

- **Google ADK Docs**: https://google.github.io/adk-docs/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Server-Sent Events**: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events
