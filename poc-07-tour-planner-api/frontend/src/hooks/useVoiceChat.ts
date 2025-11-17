/**
 * Custom hook for voice chat with the Tour Planner agent
 */

import { useState, useRef, useCallback } from 'react';
import { logger } from '@/utils/logger';
import { handleApiError } from '@/utils/errors';

interface VoiceChatState {
  isProcessing: boolean;
  isPlayingAudio: boolean;
  transcribedText: string;
  error: string | null;
}

interface UseVoiceChatOptions {
  userId: string;
  sessionId?: string;
  voice?: string;
  onTranscription?: (text: string) => void;
  onResponse?: (text: string) => void;
}

export function useVoiceChat(options: UseVoiceChatOptions) {
  const { userId, sessionId, voice = 'alloy', onTranscription, onResponse } = options;

  const [state, setState] = useState<VoiceChatState>({
    isProcessing: false,
    isPlayingAudio: false,
    transcribedText: '',
    error: null,
  });

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);

  /**
   * Send voice message and get audio response
   */
  const sendVoiceMessage = useCallback(
    async (audioBlob: Blob): Promise<void> => {
      setState((prev) => ({ ...prev, isProcessing: true, error: null }));

      try {
        logger.info('Sending voice message', {
          size: audioBlob.size,
          type: audioBlob.type,
        });

        // Create form data
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');
        formData.append('user_id', userId);
        if (sessionId) {
          formData.append('session_id', sessionId);
        }
        formData.append('voice', voice);

        // Send to backend
        const response = await fetch('/api/voice/chat', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`Voice chat failed: ${response.statusText}`);
        }

        // Get transcribed text from headers
        const transcribedText = response.headers.get('X-Transcribed-Text') || '';
        if (transcribedText) {
          logger.info('Transcribed text', { text: transcribedText });
          setState((prev) => ({ ...prev, transcribedText }));
          onTranscription?.(transcribedText);
        }

        // Get audio response
        const audioData = await response.arrayBuffer();

        if (audioData.byteLength === 0) {
          throw new Error('No audio response received');
        }

        logger.info('Received audio response', { size: audioData.byteLength });

        // Play audio response
        await playAudio(audioData);

        setState((prev) => ({ ...prev, isProcessing: false }));
      } catch (error) {
        const errorMessage = handleApiError(error);
        logger.error('Voice chat error', error);
        setState((prev) => ({
          ...prev,
          isProcessing: false,
          error: errorMessage,
        }));
      }
    },
    [userId, sessionId, voice, onTranscription, onResponse]
  );

  /**
   * Play audio response
   */
  const playAudio = useCallback(async (audioData: ArrayBuffer): Promise<void> => {
    setState((prev) => ({ ...prev, isPlayingAudio: true }));

    try {
      // Initialize audio context if needed
      if (!audioContextRef.current) {
        audioContextRef.current = new AudioContext();
      }

      const audioContext = audioContextRef.current;

      // Resume audio context if suspended
      if (audioContext.state === 'suspended') {
        await audioContext.resume();
      }

      // Decode audio data
      const audioBuffer = await audioContext.decodeAudioData(audioData);

      // Create source
      const source = audioContext.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(audioContext.destination);

      // Play audio
      return new Promise((resolve, reject) => {
        source.onended = () => {
          setState((prev) => ({ ...prev, isPlayingAudio: false }));
          resolve();
        };

        source.onerror = (error) => {
          setState((prev) => ({ ...prev, isPlayingAudio: false }));
          reject(error);
        };

        source.start(0);
      });
    } catch (error) {
      logger.error('Failed to play audio', error);
      setState((prev) => ({ ...prev, isPlayingAudio: false }));
      throw error;
    }
  }, []);

  /**
   * Stop audio playback
   */
  const stopAudio = useCallback(() => {
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    setState((prev) => ({ ...prev, isPlayingAudio: false }));
  }, []);

  /**
   * Clear error
   */
  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  return {
    state,
    sendVoiceMessage,
    stopAudio,
    clearError,
  };
}
