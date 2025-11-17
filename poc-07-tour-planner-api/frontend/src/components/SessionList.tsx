/**
 * SessionList Component
 * Displays and manages chat sessions
 */

import React from 'react';
import { Session } from '@/types';
import { formatDistanceToNow } from 'date-fns';

interface SessionListProps {
  sessions: Session[];
  currentSessionId?: string;
  onSelectSession: (sessionId: string) => void;
  onDeleteSession: (sessionId: string) => void;
  onNewSession: () => void;
  isLoading?: boolean;
}

export const SessionList: React.FC<SessionListProps> = ({
  sessions,
  currentSessionId,
  onSelectSession,
  onDeleteSession,
  onNewSession,
  isLoading = false,
}) => {
  const handleDeleteClick = (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this session?')) {
      onDeleteSession(sessionId);
    }
  };

  return (
    <div className="session-list">
      <div className="session-list-header">
        <h2>Chat History</h2>
        <button
          className="new-session-button"
          onClick={onNewSession}
          disabled={isLoading}
          aria-label="New chat"
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 20 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M10 4V16M4 10H16"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        </button>
      </div>

      <div className="session-list-items">
        {sessions.length === 0 ? (
          <div className="session-list-empty">
            <p>No chat history yet</p>
          </div>
        ) : (
          sessions.map((session) => (
            <div
              key={session.session_id}
              className={`session-item ${
                session.session_id === currentSessionId ? 'active' : ''
              }`}
              onClick={() => onSelectSession(session.session_id)}
            >
              <div className="session-item-content">
                <div className="session-item-title">
                  {session.session_id.substring(0, 20)}...
                </div>
                <div className="session-item-meta">
                  <span className="session-item-time">
                    {formatDistanceToNow(
                      new Date(session.last_update_time * 1000),
                      { addSuffix: true }
                    )}
                  </span>
                  <span className="session-item-count">
                    {session.event_count} events
                  </span>
                </div>
              </div>
              <button
                className="session-delete-button"
                onClick={(e) => handleDeleteClick(e, session.session_id)}
                aria-label="Delete session"
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 16 16"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M3 4H13M5 4V3C5 2.44772 5.44772 2 6 2H10C10.5523 2 11 2.44772 11 3V4M6 7V11M10 7V11M4 4H12V13C12 13.5523 11.5523 14 11 14H5C4.44772 14 4 13.5523 4 13V4Z"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
