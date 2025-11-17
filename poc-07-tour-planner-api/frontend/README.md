# Tour Planner Chat UI

Modern, responsive React TypeScript chat interface for the Tour Planner AI Agent with real-time streaming support via Server-Sent Events (SSE).

## Features

- 🎨 **Modern UI Design**: Clean, responsive interface with dark mode support
- 🔄 **Real-time Streaming**: Server-Sent Events (SSE) for streaming AI responses
- 💬 **Chat History**: Persistent session management with conversation history
- 🎯 **Smart Input**: Auto-resizing text input with keyboard shortcuts
- 🛠️ **Tool Visibility**: Display active tool calls during agent processing
- 📱 **Responsive**: Mobile-friendly design that works on all devices
- 🔒 **Type Safe**: Full TypeScript coverage for reliability
- 📊 **Logging**: Comprehensive logging for debugging and monitoring
- ⚡ **Error Handling**: Unified error handling with user-friendly messages
- 🧩 **Modular**: Component-based architecture for easy extension

## Tech Stack

- **React 18**: Modern React with hooks
- **TypeScript**: Full type safety
- **Vite**: Fast build tool and dev server
- **React Markdown**: Render markdown in chat messages
- **date-fns**: Date formatting utilities
- **CSS3**: Custom CSS with CSS variables for theming

## Project Structure

```
frontend/
├── src/
│   ├── components/         # React components
│   │   ├── ChatPage.tsx   # Main chat interface
│   │   ├── ChatHistory.tsx
│   │   ├── ChatMessage.tsx
│   │   ├── ChatInput.tsx
│   │   ├── SessionList.tsx
│   │   └── ErrorBoundary.tsx
│   ├── hooks/             # Custom React hooks
│   │   ├── useChat.ts     # Chat state management
│   │   └── useSessions.ts # Session management
│   ├── services/          # API services
│   │   └── api.ts         # Backend API integration
│   ├── types/             # TypeScript type definitions
│   │   └── index.ts
│   ├── utils/             # Utility functions
│   │   ├── logger.ts      # Logging utility
│   │   └── errors.ts      # Error handling
│   ├── styles/            # CSS styles
│   │   └── main.css
│   ├── App.tsx            # Root component
│   └── main.tsx           # Application entry
├── public/                # Static assets
├── index.html             # HTML template
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Running backend API (see `backend/README.md`)

### Installation

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Create environment configuration:

```bash
cp .env.example .env
```

3. Configure environment variables in `.env`:

```env
VITE_API_BASE_URL=/api
VITE_LOG_LEVEL=INFO
```

### Development

Start the development server:

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

The dev server proxies API requests to `http://localhost:8000` (configurable in `vite.config.ts`)

### Production Build

Build for production:

```bash
npm run build
```

Preview the production build:

```bash
npm run preview
```

The built files will be in the `dist/` directory.

## Configuration

### Environment Variables

- `VITE_API_BASE_URL`: Backend API base URL (default: `/api`)
- `VITE_LOG_LEVEL`: Logging level: DEBUG, INFO, WARN, ERROR (default: `INFO`)

### Vite Proxy

The dev server proxies `/api/*` requests to the backend. Configure in `vite.config.ts`:

```typescript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

## Usage

### Starting a Chat

1. The app automatically creates a session on first load
2. Type your message in the input box
3. Press Enter to send (Shift+Enter for new line)
4. Watch the AI response stream in real-time

### Managing Sessions

- Click the **+** button to create a new chat session
- Select a session from the sidebar to view its history
- Click the trash icon to delete a session
- Toggle the sidebar with the menu button

### Keyboard Shortcuts

- `Enter`: Send message
- `Shift + Enter`: New line in message

## Architecture

### Component Hierarchy

```
App
└── ErrorBoundary
    └── ChatPage
        ├── SessionList
        ├── ChatHistory
        │   └── ChatMessage[]
        └── ChatInput
```

### State Management

The app uses React hooks for state management:

- **`useChat`**: Manages chat messages, streaming, and sending
- **`useSessions`**: Manages session list and CRUD operations

### API Integration

The `services/api.ts` module provides:

- **`ChatAPI.streamMessage()`**: SSE streaming chat
- **`ChatAPI.sendMessage()`**: Non-streaming chat
- **`SessionAPI.*`**: Session management

### Error Handling

Errors are handled at multiple levels:

1. **API Layer**: Network and HTTP errors
2. **Hook Layer**: State management errors
3. **Component Layer**: User-facing error display
4. **Error Boundary**: React runtime errors

All errors are logged and displayed with user-friendly messages.

### Streaming Implementation

The app uses Server-Sent Events (SSE) for real-time streaming:

```typescript
// Stream events from backend
for await (const event of ChatAPI.streamMessage(request)) {
  if (event.type === 'content') {
    // Update message with new text
  } else if (event.type === 'tool_call') {
    // Display tool execution
  } else if (event.type === 'done') {
    // Streaming complete
  }
}
```

## Extending the UI

### Adding New Message Types

1. Update `types/index.ts` with new `StreamEvent` types
2. Handle new event types in `hooks/useChat.ts`
3. Update `ChatMessage.tsx` to render new types

### Adding New Features

The modular architecture makes it easy to extend:

- **New components**: Add to `components/`
- **New hooks**: Add to `hooks/`
- **New API endpoints**: Extend `services/api.ts`
- **New utilities**: Add to `utils/`

### Customizing Styles

The UI uses CSS variables for easy theming:

```css
:root {
  --color-primary: #3b82f6;
  --color-bg-primary: #ffffff;
  /* ... more variables */
}
```

Modify variables in `styles/main.css` to customize the theme.

## Best Practices

### Logging

Use the centralized logger:

```typescript
import { logger } from '@/utils/logger';

logger.info('User action', { userId, action });
logger.error('Operation failed', error);
```

### Error Handling

Use the error utilities:

```typescript
import { handleApiError } from '@/utils/errors';

try {
  await operation();
} catch (error) {
  const message = handleApiError(error);
  setError(message);
}
```

### Type Safety

Always define types for props and state:

```typescript
interface MyComponentProps {
  data: MyData;
  onAction: (id: string) => void;
}

export const MyComponent: React.FC<MyComponentProps> = ({ data, onAction }) => {
  // ...
};
```

## Troubleshooting

### API Connection Issues

- Ensure backend is running on port 8000
- Check proxy configuration in `vite.config.ts`
- Verify `VITE_API_BASE_URL` in `.env`

### Streaming Not Working

- Check browser console for SSE errors
- Verify backend CORS settings
- Ensure backend `/api/chat/stream` endpoint is accessible

### Build Errors

- Run `npm install` to ensure dependencies are installed
- Clear `node_modules` and reinstall if needed
- Check TypeScript errors with `npm run type-check`

## Performance Optimization

- Messages use React keys for efficient rendering
- Auto-scroll uses `scrollIntoView` for smooth UX
- CSS transitions are optimized for 60fps
- Large message histories may need virtualization (future enhancement)

## Contributing

When adding new features:

1. Follow the existing project structure
2. Add proper TypeScript types
3. Include error handling
4. Add logging for debugging
5. Update this README if needed

## License

MIT
