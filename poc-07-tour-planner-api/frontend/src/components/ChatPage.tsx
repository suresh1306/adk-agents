/**
 * ChatPage Component
 * Main chat interface with session management
 */

import React, { useState, useEffect } from 'react';
import { useChat } from '@/hooks/useChat';
import { useSessions } from '@/hooks/useSessions';
import { ChatHistory } from './ChatHistory';
import { ChatInput } from './ChatInput';
import { SessionList } from './SessionList';
import { VoiceButton } from './VoiceButton';
import { logger } from '@/utils/logger';

const DEFAULT_USER_ID = 'user_web_client';

export const ChatPage: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [userId] = useState(DEFAULT_USER_ID);

  // Session management
  const {
    sessions,
    currentSession,
    isLoading: sessionsLoading,
    error: sessionsError,
    createSession,
    selectSession,
    deleteSession,
    clearError: clearSessionsError,
  } = useSessions({ userId });

  // Chat management
  const {
    messages,
    isLoading: chatLoading,
    error: chatError,
    sendMessage,
    clearMessages,
    clearError: clearChatError,
  } = useChat({
    userId,
    sessionId: currentSession?.session_id,
    onSessionCreated: (sessionId) => {
      logger.info('New session created from chat', { sessionId });
      // The session will be added to the list on next refresh
    },
  });

  // Handle new session creation
  const handleNewSession = async () => {
    await createSession();
    clearMessages();
  };

  // Handle session selection
  const handleSelectSession = (sessionId: string) => {
    selectSession(sessionId);
    clearMessages();
  };

  // Auto-create session if none exists
  useEffect(() => {
    if (!sessionsLoading && sessions.length === 0 && !currentSession) {
      logger.info('No sessions found, creating initial session');
      createSession();
    }
  }, [sessionsLoading, sessions.length, currentSession, createSession]);

  const error = chatError || sessionsError;
  const isLoading = chatLoading || sessionsLoading;

  return (
    <div className="chat-page">
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <SessionList
          sessions={sessions}
          currentSessionId={currentSession?.session_id}
          onSelectSession={handleSelectSession}
          onDeleteSession={deleteSession}
          onNewSession={handleNewSession}
          isLoading={sessionsLoading}
        />
      </aside>

      {/* Main chat area */}
      <main className="chat-main">
        {/* Header */}
        <header className="chat-header">
          <button
            className="sidebar-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-label="Toggle sidebar"
          >
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M3 12H21M3 6H21M3 18H21"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
          </button>

          <div className="chat-header-title">
            <h1>Tour Planner AI</h1>
            {currentSession && (
              <span className="session-indicator">
                Session: {currentSession.session_id.substring(0, 12)}...
              </span>
            )}
          </div>

          <div className="chat-header-actions">
            <button
              className="clear-chat-button"
              onClick={clearMessages}
              disabled={messages.length === 0}
              aria-label="Clear chat"
            >
              Clear
            </button>
          </div>
        </header>

        {/* Error display */}
        {error && (
          <div className="error-banner">
            <div className="error-content">
              <span className="error-icon">⚠️</span>
              <span className="error-message">{error}</span>
              <button
                className="error-dismiss"
                onClick={() => {
                  clearChatError();
                  clearSessionsError();
                }}
                aria-label="Dismiss error"
              >
                ×
              </button>
            </div>
          </div>
        )}

        {/* Chat history */}
        <ChatHistory messages={messages} isLoading={isLoading} />

        {/* Input area with voice and text */}
        <div className="chat-input-area">
          <VoiceButton
            userId={userId}
            sessionId={currentSession?.session_id}
            voice="alloy"
            onTranscription={(text) => {
              // Send transcribed text as a message
              sendMessage(text);
            }}
            disabled={isLoading}
          />

          <ChatInput
            onSendMessage={sendMessage}
            disabled={isLoading}
            placeholder="Type or use voice to ask about travel destinations..."
          />
        </div>
      </main>
    </div>
  );
};
