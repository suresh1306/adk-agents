"""
POC 07: Tour Planner FastAPI with Streaming

FastAPI wrapper around the intelligent tour planner agent with:
- Streaming chat responses using Server-Sent Events (SSE)
- Session management endpoints
- Google ADK Runner pattern
- InMemorySessionService (upgrade to DatabaseSessionService for production)

Run:
  uvicorn api_server:app --reload --host 0.0.0.0 --port 8000

API Endpoints:
  POST   /api/chat/stream       - Stream chat responses (SSE)
  POST   /api/chat              - Non-streaming chat
  POST   /api/sessions          - Create new session
  GET    /api/sessions          - List all sessions for a user
  GET    /api/sessions/{id}     - Get session details
  DELETE /api/sessions/{id}     - Delete session
  GET    /api/health            - Health check
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.genai.types import Content, Part

from agent import coordinator_agent

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class ChatMessage(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")

class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="User message", min_length=1)
    user_id: str = Field(default="default_user", description="User identifier")
    session_id: Optional[str] = Field(None, description="Session ID (auto-generated if not provided)")
    stream: bool = Field(default=True, description="Enable streaming response")

class ChatResponse(BaseModel):
    """Chat response model (non-streaming)"""
    response: str = Field(..., description="Agent response")
    session_id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")

class SessionCreate(BaseModel):
    """Create session request"""
    user_id: str = Field(..., description="User identifier")
    session_id: Optional[str] = Field(None, description="Custom session ID (auto-generated if not provided)")
    initial_state: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Initial session state")

class SessionResponse(BaseModel):
    """Session response model"""
    session_id: str
    user_id: str
    app_name: str
    state: Dict[str, Any]
    last_update_time: float
    event_count: int

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    app_name: str
    session_service: str

# ============================================================================
# GLOBAL STATE
# ============================================================================

APP_NAME = "TourPlannerAPI"
session_service: Optional[InMemorySessionService] = None
runner: Optional[Runner] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    global session_service, runner

    # Startup: Initialize session service and runner
    print("🚀 Starting Tour Planner API...")
    print(f"   App: {APP_NAME}")
    print(f"   Time: {datetime.now().isoformat()}")

    # Create session service
    session_service = InMemorySessionService()
    print("✅ InMemorySessionService initialized")

    # Create runner
    runner = Runner(
        agent=coordinator_agent,
        session_service=session_service,
        app_name=APP_NAME
    )
    print("✅ Runner initialized with intelligent_tour_planner agent")
    print("🌍 Tour Planner API is ready!")

    yield

    # Shutdown
    print("👋 Shutting down Tour Planner API...")
    if runner:
        await runner.close()
    print("✅ Shutdown complete")

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Intelligent Tour Planner API",
    description="AI-powered travel planning assistant with streaming support",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# STREAMING HELPER
# ============================================================================

async def event_stream_generator(
    runner: Runner,
    user_message: Content,
    user_id: str,
    session_id: str
):
    """
    Generator that yields Server-Sent Events (SSE) from the agent

    SSE format:
      data: {"type": "content", "text": "Hello"}

      data: {"type": "tool_call", "tool": "search_destination"}

      data: {"type": "done"}
    """
    try:
        # Stream events from runner
        async for event in runner.run_async(
            session_id=session_id,
            user_id=user_id,
            new_message=user_message
        ):
            # Process different event types
            event_data = {}

            # Check for content (agent response text)
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            event_data = {
                                "type": "content",
                                "text": part.text,
                                "role": event.content.role if hasattr(event.content, 'role') else "assistant"
                            }
                            yield f"data: {json.dumps(event_data)}\n\n"

            # Check for tool calls
            elif hasattr(event, 'tool_call'):
                event_data = {
                    "type": "tool_call",
                    "tool": event.tool_call.name if hasattr(event.tool_call, 'name') else "unknown",
                    "status": "executing"
                }
                yield f"data: {json.dumps(event_data)}\n\n"

            # Check for tool results
            elif hasattr(event, 'tool_result'):
                event_data = {
                    "type": "tool_result",
                    "tool": event.tool_result.name if hasattr(event.tool_result, 'name') else "unknown",
                    "status": "completed"
                }
                yield f"data: {json.dumps(event_data)}\n\n"

        # Send completion event
        yield f"data: {json.dumps({'type': 'done', 'session_id': session_id})}\n\n"

    except Exception as e:
        # Send error event
        error_data = {
            "type": "error",
            "message": str(e),
            "error_type": type(e).__name__
        }
        yield f"data: {json.dumps(error_data)}\n\n"

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        app_name=APP_NAME,
        session_service="InMemorySessionService"
    )

@app.post("/api/sessions", response_model=SessionResponse)
async def create_session(request: SessionCreate):
    """
    Create a new session

    Example:
      POST /api/sessions
      {
        "user_id": "user_123",
        "initial_state": {"temp:language": "en"}
      }
    """
    if not session_service:
        raise HTTPException(status_code=500, detail="Session service not initialized")

    # Generate session ID if not provided
    sid = request.session_id or f"session_{uuid.uuid4().hex[:16]}"

    # Create session
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=request.user_id,
        session_id=sid,
        state=request.initial_state or {}
    )

    return SessionResponse(
        session_id=session.id,
        user_id=session.user_id,
        app_name=session.app_name,
        state=session.state,
        last_update_time=session.last_update_time,
        event_count=len(session.events)
    )

@app.get("/api/sessions", response_model=List[SessionResponse])
async def list_sessions(user_id: str):
    """
    List all sessions for a user

    Example:
      GET /api/sessions?user_id=user_123
    """
    if not session_service:
        raise HTTPException(status_code=500, detail="Session service not initialized")

    sessions = await session_service.list_sessions(
        app_name=APP_NAME,
        user_id=user_id
    )

    return [
        SessionResponse(
            session_id=s.id,
            user_id=s.user_id,
            app_name=s.app_name,
            state=s.state,
            last_update_time=s.last_update_time,
            event_count=len(s.events)
        )
        for s in sessions
    ]

@app.get("/api/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, user_id: str):
    """
    Get session details

    Example:
      GET /api/sessions/session_abc?user_id=user_123
    """
    if not session_service:
        raise HTTPException(status_code=500, detail="Session service not initialized")

    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id
    )

    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    return SessionResponse(
        session_id=session.id,
        user_id=session.user_id,
        app_name=session.app_name,
        state=session.state,
        last_update_time=session.last_update_time,
        event_count=len(session.events)
    )

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str, user_id: str):
    """
    Delete a session

    Example:
      DELETE /api/sessions/session_abc?user_id=user_123
    """
    if not session_service:
        raise HTTPException(status_code=500, detail="Session service not initialized")

    await session_service.delete_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id
    )

    return {"status": "deleted", "session_id": session_id}

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat responses using Server-Sent Events (SSE)

    Example:
      POST /api/chat/stream
      {
        "message": "I want to visit Japan",
        "user_id": "user_123",
        "session_id": "session_abc"
      }

    Response (SSE):
      data: {"type": "content", "text": "Wonderful! Let me gather..."}

      data: {"type": "tool_call", "tool": "search_destination"}

      data: {"type": "content", "text": "Japan offers amazing..."}

      data: {"type": "done", "session_id": "session_abc"}
    """
    if not runner or not session_service:
        raise HTTPException(status_code=500, detail="Service not initialized")

    # Generate session ID if not provided
    session_id = request.session_id or f"session_{uuid.uuid4().hex[:16]}"

    # Ensure session exists
    existing_session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=request.user_id,
        session_id=session_id
    )

    if not existing_session:
        # Create new session
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=request.user_id,
            session_id=session_id,
            state={}
        )

    # Create user message
    user_message = Content(
        role='user',
        parts=[Part(text=request.message)]
    )

    # Return streaming response
    return StreamingResponse(
        event_stream_generator(runner, user_message, request.user_id, session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable buffering in nginx
        }
    )

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Non-streaming chat endpoint (waits for complete response)

    Example:
      POST /api/chat
      {
        "message": "I want to visit Japan",
        "user_id": "user_123",
        "session_id": "session_abc"
      }

    Response:
      {
        "response": "Wonderful! Let me gather information about Japan...",
        "session_id": "session_abc",
        "user_id": "user_123"
      }
    """
    if not runner or not session_service:
        raise HTTPException(status_code=500, detail="Service not initialized")

    # Generate session ID if not provided
    session_id = request.session_id or f"session_{uuid.uuid4().hex[:16]}"

    # Ensure session exists
    existing_session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=request.user_id,
        session_id=session_id
    )

    if not existing_session:
        # Create new session
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=request.user_id,
            session_id=session_id,
            state={}
        )

    # Create user message
    user_message = Content(
        role='user',
        parts=[Part(text=request.message)]
    )

    # Collect all response text
    response_text = []

    try:
        async for event in runner.run_async(
            session_id=session_id,
            user_id=request.user_id,
            new_message=user_message
        ):
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_text.append(part.text)

        return ChatResponse(
            response="".join(response_text),
            session_id=session_id,
            user_id=request.user_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Intelligent Tour Planner API",
        "version": "1.0.0",
        "description": "AI-powered travel planning assistant with streaming support",
        "endpoints": {
            "health": "GET /api/health",
            "chat_stream": "POST /api/chat/stream (SSE streaming)",
            "chat": "POST /api/chat (non-streaming)",
            "create_session": "POST /api/sessions",
            "list_sessions": "GET /api/sessions?user_id={user_id}",
            "get_session": "GET /api/sessions/{session_id}?user_id={user_id}",
            "delete_session": "DELETE /api/sessions/{session_id}?user_id={user_id}"
        },
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
