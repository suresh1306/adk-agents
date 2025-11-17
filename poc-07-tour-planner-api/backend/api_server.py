"""
POC 07: Tour Planner FastAPI with Streaming and Voice

FastAPI wrapper around the intelligent tour planner agent with:
- Streaming chat responses using Server-Sent Events (SSE)
- Voice agent capabilities (Speech-to-Text, Text-to-Speech)
- Session management endpoints
- Google ADK Runner pattern
- InMemorySessionService (upgrade to DatabaseSessionService for production)

Run:
  uvicorn api_server:app --reload --host 0.0.0.0 --port 8000

API Endpoints:
  POST   /api/chat/stream       - Stream chat responses (SSE)
  POST   /api/chat              - Non-streaming chat
  POST   /api/voice/transcribe  - Transcribe audio to text
  POST   /api/voice/synthesize  - Convert text to speech
  POST   /api/voice/chat        - Voice chat with streaming audio response
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

from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, Response
from pydantic import BaseModel, Field
import re

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.genai.types import Content, Part

from agent import coordinator_agent
from voice_service import voice_service, AudioTranscription

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def sanitize_header_value(text: str) -> str:
    """
    Sanitize text for use in HTTP headers
    - Remove newlines and replace with spaces
    - Remove non-ASCII characters
    - Remove control characters
    """
    if not text:
        return ""

    # Replace newlines and carriage returns with spaces
    text = text.replace('\n', ' ').replace('\r', ' ')

    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)

    # Keep only ASCII printable characters (32-126)
    text = ''.join(char if 32 <= ord(char) <= 126 else ' ' for char in text)

    # Trim and return
    return text.strip()

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
    voice_enabled: bool

class VoiceTranscriptionResponse(BaseModel):
    """Voice transcription response"""
    text: str
    language: Optional[str] = None
    duration: Optional[float] = None

class VoiceSynthesisRequest(BaseModel):
    """Voice synthesis request"""
    text: str
    voice: str = Field(
        default="Jennifer-PlayAI",
        description="PlayAI voice (e.g., Jennifer-PlayAI, Atlas-PlayAI, Celeste-PlayAI)"
    )
    model: str = Field(default="playai-tts", description="Model: playai-tts (Groq TTS)")

class VoiceChatRequest(BaseModel):
    """Voice chat request"""
    user_id: str
    session_id: Optional[str] = None
    voice: str = Field(
        default="Jennifer-PlayAI",
        description="PlayAI voice for response (e.g., Jennifer-PlayAI, Atlas-PlayAI)"
    )

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
        session_service="InMemorySessionService",
        voice_enabled=voice_service.is_voice_enabled()
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

    # list_sessions returns tuples of (app_name, user_id, session_id)
    session_keys = await session_service.list_sessions(
        app_name=APP_NAME,
        user_id=user_id
    )

    # Fetch full session details for each session
    session_responses = []
    for session_key in session_keys:
        # session_key is a tuple: (app_name, user_id, session_id)
        if isinstance(session_key, tuple) and len(session_key) == 3:
            _, _, session_id = session_key
        else:
            # Fallback if format is different
            continue

        session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id
        )

        if session:
            session_responses.append(
                SessionResponse(
                    session_id=session.id,
                    user_id=session.user_id,
                    app_name=session.app_name,
                    state=session.state,
                    last_update_time=session.last_update_time,
                    event_count=len(session.events)
                )
            )

    return session_responses

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
# VOICE ENDPOINTS
# ============================================================================

@app.post("/api/voice/transcribe", response_model=VoiceTranscriptionResponse)
async def transcribe_audio(
    audio: UploadFile = File(..., description="Audio file to transcribe")
):
    """
    Transcribe audio to text using Groq Whisper

    Example:
      POST /api/voice/transcribe
      Content-Type: multipart/form-data

      audio: <audio file>

    Returns:
      {
        "text": "transcribed text",
        "language": "en",
        "duration": 5.2
      }
    """
    try:
        # Read audio file
        audio_data = await audio.read()

        # Get content type
        content_type = audio.content_type or "audio/webm"

        # Transcribe
        transcription = await voice_service.transcribe_audio(audio_data, content_type)

        return VoiceTranscriptionResponse(
            text=transcription.text,
            language=transcription.language,
            duration=transcription.duration
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@app.post("/api/voice/synthesize")
async def synthesize_speech(request: VoiceSynthesisRequest):
    """
    Convert text to speech using Groq PlayAI TTS

    Example:
      POST /api/voice/synthesize
      {
        "text": "Hello, how can I help you plan your trip?",
        "voice": "alloy",
        "model": "playai-tts"
      }

    Returns:
      Audio file (MP3)
    """
    try:
        audio_bytes = await voice_service.synthesize_speech(
            text=request.text,
            voice=request.voice,
            model=request.model
        )

        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {str(e)}")

@app.post("/api/voice/chat")
async def voice_chat(
    audio: UploadFile = File(..., description="Audio message from user"),
    user_id: str = Form(..., description="User ID"),
    session_id: Optional[str] = Form(None, description="Session ID"),
    voice: str = Form("Jennifer-PlayAI", description="Voice for response (PlayAI format)")
):
    """
    Voice chat: transcribe audio, process with agent, return audio response

    Example:
      POST /api/voice/chat
      Content-Type: multipart/form-data

      audio: <audio file>
      user_id: user_123
      session_id: session_abc (optional)
      voice: alloy

    Returns:
      Streaming audio response (MP3)
    """
    if not runner or not session_service:
        raise HTTPException(status_code=500, detail="Service not initialized")

    try:
        # 1. Transcribe audio to text
        audio_data = await audio.read()
        content_type = audio.content_type or "audio/webm"

        text = await voice_service.process_voice_message(audio_data, content_type)

        if not text.strip():
            raise HTTPException(status_code=400, detail="No speech detected in audio")

        # 2. Generate session ID if not provided
        sid = session_id or f"session_{uuid.uuid4().hex[:16]}"

        # 3. Ensure session exists
        existing_session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=sid
        )

        if not existing_session:
            await session_service.create_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=sid,
                state={}
            )

        # 4. Process message with agent
        user_message = Content(
            role='user',
            parts=[Part(text=text)]
        )

        response_text = []
        async for event in runner.run_async(
            session_id=sid,
            user_id=user_id,
            new_message=user_message
        ):
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_text.append(part.text)

        full_response = "".join(response_text)

        if not full_response.strip():
            full_response = "I apologize, I didn't understand that. Could you please rephrase?"

        # 5. Determine if response is long - if so, generate summary for voice
        is_long = voice_service.is_long_response(full_response)
        spoken_text = full_response

        if is_long:
            # Generate short summary for voice output
            spoken_text = await voice_service.generate_voice_summary(
                full_response,
                context="travel planning"
            )

        # 6. Stream TTS audio response (summary if long, full text if short)
        async def audio_stream():
            async for chunk in voice_service.synthesize_speech_streaming(spoken_text, voice):
                yield chunk

        return StreamingResponse(
            audio_stream(),
            media_type="audio/mpeg",
            headers={
                "X-Session-ID": sid,
                "X-Transcribed-Text": sanitize_header_value(text[:200]),  # User's transcribed input
                "X-Full-Response": sanitize_header_value(full_response[:500]),  # Full response text
                "X-Spoken-Text": sanitize_header_value(spoken_text[:200]),  # What was actually spoken
                "X-Is-Summary": "true" if is_long else "false",
                "Content-Disposition": "inline; filename=response.mp3"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice chat failed: {str(e)}")

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
