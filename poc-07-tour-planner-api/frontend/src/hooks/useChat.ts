/**
 * Custom hook for chat functionality with streaming support
 */

import { useState, useCallback, useRef } from 'react';
import { Message, ChatState, StreamEvent } from '@/types';
import { ChatAPI } from '@/services/api';
import { handleApiError } from '@/utils/errors';
import { logger } from '@/utils/logger';

interface UseChatOptions {
  userId: string;
  sessionId?: string;
  onSessionCreated?: (sessionId: string) => void;
}

interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  chatState: ChatState;
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
  clearError: () => void;
}

export function useChat(options: UseChatOptions): UseChatReturn {
  const { userId, sessionId: initialSessionId, onSessionCreated } = options;

  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [chatState, setChatState] = useState<ChatState>('idle');
  const sessionIdRef = useRef<string | undefined>(initialSessionId);
  const abortControllerRef = useRef<AbortController | null>(null);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
    setChatState('idle');
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isLoading) {
        return;
      }

      // Create user message
      const userMessage: Message = {
        id: `msg_${Date.now()}_user`,
        role: 'user',
        content: content.trim(),
        timestamp: new Date(),
      };

      // Add user message to chat
      setMessages(prev => [...prev, userMessage]);
      setIsLoading(true);
      setChatState('loading');
      setError(null);

      // Create placeholder for assistant message
      const assistantMessageId = `msg_${Date.now()}_assistant`;
      const assistantMessage: Message = {
        id: assistantMessageId,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        isStreaming: true,
        toolCalls: [],
      };

      setMessages(prev => [...prev, assistantMessage]);
      setChatState('streaming');

      try {
        // Stream the response
        const stream = ChatAPI.streamMessage({
          message: content.trim(),
          user_id: userId,
          session_id: sessionIdRef.current,
          stream: true,
        });

        let accumulatedContent = '';
        const toolCalls: Message['toolCalls'] = [];

        for await (const event of stream) {
          logger.debug('Stream event', event);

          if (event.type === 'content' && event.text) {
            accumulatedContent += event.text;

            // Update the assistant message with accumulated content
            setMessages(prev =>
              prev.map(msg =>
                msg.id === assistantMessageId
                  ? { ...msg, content: accumulatedContent }
                  : msg
              )
            );
          } else if (event.type === 'tool_call' && event.tool) {
            // Track tool calls
            toolCalls.push({
              name: event.tool,
              status: event.status as 'executing' | 'completed',
              timestamp: new Date(),
            });

            setMessages(prev =>
              prev.map(msg =>
                msg.id === assistantMessageId ? { ...msg, toolCalls } : msg
              )
            );
          } else if (event.type === 'done') {
            // Stream completed
            if (event.session_id && !sessionIdRef.current) {
              sessionIdRef.current = event.session_id;
              onSessionCreated?.(event.session_id);
            }

            // Mark message as no longer streaming
            setMessages(prev =>
              prev.map(msg =>
                msg.id === assistantMessageId
                  ? { ...msg, isStreaming: false }
                  : msg
              )
            );
            break;
          } else if (event.type === 'error') {
            throw new Error(event.message || 'Streaming error occurred');
          }
        }

        setChatState('idle');
      } catch (err) {
        const errorMessage = handleApiError(err);
        setError(errorMessage);
        setChatState('error');

        // Remove the incomplete assistant message
        setMessages(prev => prev.filter(msg => msg.id !== assistantMessageId));

        logger.error('Chat error', err);
      } finally {
        setIsLoading(false);
      }
    },
    [userId, isLoading, onSessionCreated]
  );

  return {
    messages,
    isLoading,
    error,
    chatState,
    sendMessage,
    clearMessages,
    clearError,
  };
}
