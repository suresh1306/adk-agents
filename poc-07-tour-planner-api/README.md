# POC-07: Tour Planner AI with Modern Chat UI

A full-stack intelligent tour planning assistant with:
- **Backend**: FastAPI with Google ADK agents and streaming SSE support
- **Frontend**: Modern React TypeScript chat UI with real-time streaming

## Project Structure

```
poc-07-tour-planner-api/
├── backend/                    # Python FastAPI backend
│   ├── agent.py               # Tour planner agent with sub-agents
│   ├── api_server.py          # FastAPI server with SSE streaming
│   ├── tools.py               # Agent tools (search, weather, etc.)
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example           # Environment configuration
│   └── README.md              # Backend documentation
│
├── frontend/                   # React TypeScript UI
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── hooks/             # Custom hooks (useChat, useSessions)
│   │   ├── services/          # API integration with SSE
│   │   ├── types/             # TypeScript definitions
│   │   ├── utils/             # Logging, error handling
│   │   └── styles/            # CSS styling
│   ├── package.json
│   ├── vite.config.ts
│   └── README.md              # Frontend documentation
│
└── README.md                   # This file
```

## Features

### Backend Features

✅ **Intelligent Agent System**
- Coordinator agent with specialized sub-agents
- Tool calling for destination search, weather, activities
- Session management with conversation history
- Streaming responses via Server-Sent Events (SSE)

✅ **RESTful API**
- `/api/chat/stream` - Streaming chat with SSE
- `/api/chat` - Non-streaming chat
- `/api/sessions/*` - Session CRUD operations
- `/api/health` - Health check endpoint

✅ **Production Ready**
- CORS support for frontend integration
- Error handling and logging
- Async/await throughout
- InMemorySessionService (upgradeable to database)

### Frontend Features

✅ **Modern Chat Interface**
- Real-time message streaming
- Markdown rendering with syntax highlighting
- Auto-resizing input box
- Responsive design (mobile-friendly)

✅ **Session Management**
- Create and manage multiple chat sessions
- Session history with timestamps
- Delete sessions
- Auto-save conversations

✅ **Developer Experience**
- Full TypeScript coverage
- Modular component architecture
- Custom hooks for state management
- Comprehensive error handling
- Centralized logging
- Hot module replacement (HMR)

✅ **User Experience**
- Smooth animations and transitions
- Loading indicators
- Tool call visibility
- Error messages
- Dark mode support
- Keyboard shortcuts

## Quick Start

### Prerequisites

- **Backend**: Python 3.11+, Google Cloud credentials
- **Frontend**: Node.js 18+, npm

### 1. Start the Backend

```bash
cd backend

# Set up Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Google Cloud credentials

# Start the API server
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

### 2. Start the Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

### 3. Use the Application

1. Open `http://localhost:3000` in your browser
2. Start chatting with the Tour Planner AI
3. Try queries like:
   - "I want to plan a trip to Japan"
   - "What's the weather like in Paris?"
   - "Suggest family-friendly activities in London"

## Architecture

### Communication Flow

```
User Browser
    ↓
React UI (Port 3000)
    ↓
Vite Dev Proxy (/api → :8000)
    ↓
FastAPI Server (Port 8000)
    ↓
Google ADK Runner
    ↓
Coordinator Agent
    ↓
Sub-Agents (Search, Weather, Activities)
    ↓
External APIs / Tools
```

### Streaming Architecture

```
1. User sends message → POST /api/chat/stream
2. Backend creates SSE connection
3. Agent processes request:
   - Calls tools (search_destination, get_weather, etc.)
   - Generates response chunks
4. Server sends SSE events:
   - type: 'content' → Text chunks
   - type: 'tool_call' → Tool execution
   - type: 'done' → Complete
5. Frontend updates UI in real-time
```

### Technology Stack

**Backend**
- FastAPI - High-performance async web framework
- Google ADK (Agent Development Kit) - Agent framework
- Google Gemini - LLM for agent intelligence
- Pydantic - Data validation
- Uvicorn - ASGI server

**Frontend**
- React 18 - UI library
- TypeScript - Type safety
- Vite - Build tool and dev server
- React Markdown - Markdown rendering
- date-fns - Date formatting

## Development

### Backend Development

```bash
cd backend

# Run with auto-reload
uvicorn api_server:app --reload --port 8000

# Run tests (if available)
pytest

# Type checking
mypy .
```

### Frontend Development

```bash
cd frontend

# Development server
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Production build
npm run build

# Preview production build
npm run preview
```

## Configuration

### Backend Configuration (backend/.env)

```env
# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# API Keys
GOOGLE_API_KEY=your-api-key

# Server
HOST=0.0.0.0
PORT=8000
```

### Frontend Configuration (frontend/.env)

```env
# API
VITE_API_BASE_URL=/api

# Logging
VITE_LOG_LEVEL=INFO
```

## API Documentation

### Chat Endpoints

**Stream Chat (SSE)**
```http
POST /api/chat/stream
Content-Type: application/json

{
  "message": "Plan a trip to Japan",
  "user_id": "user_123",
  "session_id": "session_abc"  // optional
}
```

Response: Server-Sent Events stream

**Non-Streaming Chat**
```http
POST /api/chat
Content-Type: application/json

{
  "message": "Plan a trip to Japan",
  "user_id": "user_123",
  "session_id": "session_abc"  // optional
}
```

### Session Endpoints

- `POST /api/sessions` - Create session
- `GET /api/sessions?user_id={id}` - List sessions
- `GET /api/sessions/{id}?user_id={uid}` - Get session
- `DELETE /api/sessions/{id}?user_id={uid}` - Delete session

### Health Check

```http
GET /api/health
```

See `backend/README.md` for complete API documentation.

## Extending the Application

### Adding New Agent Tools

1. Define tool in `backend/tools.py`
2. Add tool to agent in `backend/agent.py`
3. Tool calls will automatically appear in UI

### Adding New UI Features

1. Create component in `frontend/src/components/`
2. Add types in `frontend/src/types/`
3. Integrate in `ChatPage.tsx`

### Adding New API Endpoints

1. Add endpoint in `backend/api_server.py`
2. Add types in `frontend/src/types/`
3. Add service method in `frontend/src/services/api.ts`
4. Create hook if needed in `frontend/src/hooks/`

## Deployment

### Backend Deployment

Options:
- **Google Cloud Run**: Containerize and deploy
- **Google App Engine**: Deploy with `app.yaml`
- **Kubernetes**: Deploy with k8s manifests
- **VM**: Run with systemd service

### Frontend Deployment

Options:
- **Static Hosting**: Build and deploy `dist/` to:
  - Vercel
  - Netlify
  - Firebase Hosting
  - Google Cloud Storage + CDN
- **Container**: Serve with nginx

### Full Stack Deployment

Recommended: Deploy backend and frontend separately
- Backend: Cloud Run / App Engine
- Frontend: Vercel / Netlify
- Configure CORS and API URL

## Troubleshooting

### Backend Issues

**Agent not responding**
- Check Google Cloud credentials
- Verify API keys in `.env`
- Check logs for errors

**CORS errors**
- Ensure CORS middleware is configured
- Check `allow_origins` in `api_server.py`

### Frontend Issues

**Cannot connect to API**
- Ensure backend is running on port 8000
- Check proxy config in `vite.config.ts`
- Verify `VITE_API_BASE_URL` in `.env`

**Streaming not working**
- Check browser console for SSE errors
- Verify `/api/chat/stream` endpoint
- Check network tab for event-stream

### General Issues

**Port conflicts**
- Backend: Change port in `uvicorn` command
- Frontend: Change `server.port` in `vite.config.ts`

**Missing dependencies**
- Backend: `pip install -r requirements.txt`
- Frontend: `npm install`

## Best Practices

### Code Organization

- ✅ Keep components small and focused
- ✅ Use TypeScript for type safety
- ✅ Centralize API calls in service layer
- ✅ Use custom hooks for shared logic
- ✅ Follow existing naming conventions

### Error Handling

- ✅ Use unified error handling utilities
- ✅ Log errors with context
- ✅ Show user-friendly error messages
- ✅ Handle network failures gracefully

### Performance

- ✅ Use React keys for list rendering
- ✅ Implement proper loading states
- ✅ Optimize re-renders with useMemo/useCallback
- ✅ Keep API payloads small

### Security

- ✅ Validate user input
- ✅ Sanitize displayed content
- ✅ Use environment variables for secrets
- ✅ Configure CORS appropriately
- ✅ Implement rate limiting (production)

## Contributing

1. Follow the existing code style
2. Add TypeScript types for new code
3. Include error handling and logging
4. Update documentation
5. Test changes thoroughly

## Future Enhancements

### Backend
- [ ] Database session storage (PostgreSQL/Firestore)
- [ ] User authentication and authorization
- [ ] Rate limiting and quotas
- [ ] Metrics and monitoring
- [ ] WebSocket support for bi-directional communication
- [ ] Caching layer for tool responses

### Frontend
- [ ] Message virtualization for long conversations
- [ ] Rich media support (images, maps)
- [ ] Voice input support
- [ ] Export conversation feature
- [ ] Conversation search
- [ ] User preferences and settings
- [ ] PWA support for offline access

### DevOps
- [ ] Docker Compose for local development
- [ ] CI/CD pipeline
- [ ] Automated testing
- [ ] Performance monitoring
- [ ] Error tracking (Sentry)

## License

MIT

## Support

For issues and questions:
- Backend: See `backend/README.md`
- Frontend: See `frontend/README.md`
- General: Create an issue in the repository
