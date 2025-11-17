/**
 * ChatMessage Component
 * Displays a single chat message with markdown support
 */

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Message } from '@/types';
import { formatDistanceToNow } from 'date-fns';

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div
      className={`chat-message ${isUser ? 'user-message' : 'assistant-message'}`}
      data-message-id={message.id}
    >
      <div className="message-header">
        <span className="message-role">{isUser ? 'You' : 'Assistant'}</span>
        <span className="message-timestamp">
          {formatDistanceToNow(message.timestamp, { addSuffix: true })}
        </span>
      </div>

      <div className="message-content">
        {message.isStreaming && !message.content ? (
          <div className="streaming-indicator">
            <span className="dot"></span>
            <span className="dot"></span>
            <span className="dot"></span>
          </div>
        ) : (
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {message.content}
          </ReactMarkdown>
        )}

        {message.isStreaming && message.content && (
          <span className="streaming-cursor">▊</span>
        )}
      </div>

      {message.toolCalls && message.toolCalls.length > 0 && (
        <div className="tool-calls">
          {message.toolCalls.map((tool, index) => (
            <div key={index} className={`tool-call tool-${tool.status}`}>
              <span className="tool-icon">🔧</span>
              <span className="tool-name">{tool.name}</span>
              <span className="tool-status">{tool.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
