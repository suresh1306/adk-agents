/**
 * ChatHistory Component
 * Displays the conversation with auto-scroll
 */

import React, { useRef, useEffect } from 'react';
import { Message } from '@/types';
import { ChatMessage } from './ChatMessage';

interface ChatHistoryProps {
  messages: Message[];
  isLoading?: boolean;
}

export const ChatHistory: React.FC<ChatHistoryProps> = ({ messages, isLoading }) => {
  const bottomRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  return (
    <div className="chat-history" ref={containerRef}>
      {messages.length === 0 ? (
        <div className="chat-empty-state">
          <div className="empty-state-icon">💬</div>
          <h2>Start a conversation</h2>
          <p>Ask me anything about travel planning!</p>
          <div className="suggestion-chips">
            <button className="suggestion-chip">
              Plan a trip to Japan
            </button>
            <button className="suggestion-chip">
              Best destinations for adventure
            </button>
            <button className="suggestion-chip">
              Family-friendly vacation ideas
            </button>
          </div>
        </div>
      ) : (
        <>
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
          <div ref={bottomRef} />
        </>
      )}
    </div>
  );
};
