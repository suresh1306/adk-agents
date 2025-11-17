/**
 * Custom hook for session management
 */

import { useState, useEffect, useCallback } from 'react';
import { Session } from '@/types';
import { SessionAPI } from '@/services/api';
import { handleApiError } from '@/utils/errors';
import { logger } from '@/utils/logger';

interface UseSessionsOptions {
  userId: string;
  autoLoad?: boolean;
}

interface UseSessionsReturn {
  sessions: Session[];
  currentSession: Session | null;
  isLoading: boolean;
  error: string | null;
  createSession: () => Promise<Session | null>;
  loadSessions: () => Promise<void>;
  selectSession: (sessionId: string) => void;
  deleteSession: (sessionId: string) => Promise<void>;
  clearError: () => void;
}

export function useSessions(options: UseSessionsOptions): UseSessionsReturn {
  const { userId, autoLoad = true } = options;

  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSession, setCurrentSession] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const loadSessions = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const fetchedSessions = await SessionAPI.list(userId);

      // Sort sessions by last update time (most recent first)
      const sortedSessions = fetchedSessions.sort(
        (a, b) => b.last_update_time - a.last_update_time
      );

      setSessions(sortedSessions);
      logger.info('Sessions loaded', { count: sortedSessions.length });
    } catch (err) {
      const errorMessage = handleApiError(err);
      setError(errorMessage);
      logger.error('Failed to load sessions', err);
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  const createSession = useCallback(async (): Promise<Session | null> => {
    setIsLoading(true);
    setError(null);

    try {
      const newSession = await SessionAPI.create({
        user_id: userId,
        initial_state: {},
      });

      setSessions(prev => [newSession, ...prev]);
      setCurrentSession(newSession);
      logger.info('Session created', { sessionId: newSession.session_id });

      return newSession;
    } catch (err) {
      const errorMessage = handleApiError(err);
      setError(errorMessage);
      logger.error('Failed to create session', err);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  const selectSession = useCallback(
    (sessionId: string) => {
      const session = sessions.find(s => s.session_id === sessionId);
      if (session) {
        setCurrentSession(session);
        logger.info('Session selected', { sessionId });
      }
    },
    [sessions]
  );

  const deleteSession = useCallback(
    async (sessionId: string) => {
      setIsLoading(true);
      setError(null);

      try {
        await SessionAPI.delete(sessionId, userId);
        setSessions(prev => prev.filter(s => s.session_id !== sessionId));

        if (currentSession?.session_id === sessionId) {
          setCurrentSession(null);
        }

        logger.info('Session deleted', { sessionId });
      } catch (err) {
        const errorMessage = handleApiError(err);
        setError(errorMessage);
        logger.error('Failed to delete session', err);
      } finally {
        setIsLoading(false);
      }
    },
    [userId, currentSession]
  );

  // Auto-load sessions on mount
  useEffect(() => {
    if (autoLoad) {
      loadSessions();
    }
  }, [autoLoad, loadSessions]);

  return {
    sessions,
    currentSession,
    isLoading,
    error,
    createSession,
    loadSessions,
    selectSession,
    deleteSession,
    clearError,
  };
}
