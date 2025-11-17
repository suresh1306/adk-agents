/**
 * API Service Layer
 * Handles all communication with the Tour Planner backend
 */

import {
  ChatRequest,
  ChatResponse,
  Session,
  SessionCreate,
  StreamEvent,
  HealthStatus,
} from '@/types';
import { ApiException, NetworkException, parseApiError } from '@/utils/errors';
import { logger } from '@/utils/logger';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

/**
 * Base fetch wrapper with error handling
 */
async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  logger.debug(`API Request: ${options?.method || 'GET'} ${url}`, options?.body);

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw await parseApiError(response);
    }

    const data = await response.json();
    logger.debug(`API Response: ${url}`, data);
    return data;
  } catch (error) {
    if (error instanceof ApiException) {
      throw error;
    }
    logger.error('Network error', error);
    throw new NetworkException('Failed to connect to server', error);
  }
}

/**
 * Health Check
 */
export async function checkHealth(): Promise<HealthStatus> {
  return apiFetch<HealthStatus>('/health');
}

/**
 * Session Management
 */
export const SessionAPI = {
  /**
   * Create a new session
   */
  async create(request: SessionCreate): Promise<Session> {
    return apiFetch<Session>('/sessions', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  /**
   * List all sessions for a user
   */
  async list(userId: string): Promise<Session[]> {
    return apiFetch<Session[]>(`/sessions?user_id=${encodeURIComponent(userId)}`);
  },

  /**
   * Get session details
   */
  async get(sessionId: string, userId: string): Promise<Session> {
    return apiFetch<Session>(
      `/sessions/${encodeURIComponent(sessionId)}?user_id=${encodeURIComponent(userId)}`
    );
  },

  /**
   * Delete a session
   */
  async delete(sessionId: string, userId: string): Promise<void> {
    return apiFetch<void>(
      `/sessions/${encodeURIComponent(sessionId)}?user_id=${encodeURIComponent(userId)}`,
      { method: 'DELETE' }
    );
  },
};

/**
 * Chat API
 */
export const ChatAPI = {
  /**
   * Send a chat message (non-streaming)
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    return apiFetch<ChatResponse>('/chat', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  /**
   * Stream chat messages using Server-Sent Events
   * Returns an async generator that yields StreamEvents
   */
  async *streamMessage(request: ChatRequest): AsyncGenerator<StreamEvent, void, unknown> {
    const url = `${API_BASE_URL}/chat/stream`;
    logger.info('Starting SSE stream', { url, request });

    let response: Response;
    try {
      response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw await parseApiError(response);
      }
    } catch (error) {
      logger.error('Failed to initiate stream', error);
      throw error;
    }

    // Get the response body reader
    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('Response body is not readable');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          logger.info('Stream completed');
          break;
        }

        // Decode the chunk and add to buffer
        buffer += decoder.decode(value, { stream: true });

        // Process complete SSE messages
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim();
            if (data) {
              try {
                const event: StreamEvent = JSON.parse(data);
                logger.debug('Stream event received', event);
                yield event;

                // Stop if we receive a done or error event
                if (event.type === 'done' || event.type === 'error') {
                  return;
                }
              } catch (error) {
                logger.warn('Failed to parse SSE data', { data, error });
              }
            }
          }
        }
      }
    } catch (error) {
      logger.error('Stream reading error', error);
      throw new NetworkException('Stream connection lost', error);
    } finally {
      reader.releaseLock();
    }
  },
};

export default {
  checkHealth,
  SessionAPI,
  ChatAPI,
};
