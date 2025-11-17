/**
 * Custom hook for voice recording with VAD
 */

import { useState, useRef, useCallback } from 'react';
import { VoiceActivityDetector } from '@/utils/vad';
import { logger } from '@/utils/logger';

export interface VoiceRecorderState {
  isRecording: boolean;
  isSpeaking: boolean;
  volume: number;
  duration: number;
  error: string | null;
}

export interface UseVoiceRecorderReturn {
  state: VoiceRecorderState;
  startRecording: () => Promise<void>;
  stopRecording: () => Promise<Blob | null>;
  cancelRecording: () => void;
}

export function useVoiceRecorder(): UseVoiceRecorderReturn {
  const [state, setState] = useState<VoiceRecorderState>({
    isRecording: false,
    isSpeaking: false,
    volume: 0,
    duration: 0,
    error: null,
  });

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const vadRef = useRef<VoiceActivityDetector | null>(null);
  const startTimeRef = useRef<number>(0);
  const durationIntervalRef = useRef<number | null>(null);

  const startRecording = useCallback(async () => {
    try {
      logger.info('Starting voice recording...');

      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          channelCount: 1,
          sampleRate: 16000,
        },
      });

      streamRef.current = stream;
      audioChunksRef.current = [];

      // Create MediaRecorder
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : 'audio/webm';

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType,
        audioBitsPerSecond: 128000,
      });

      mediaRecorderRef.current = mediaRecorder;

      // Handle data available
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      // Initialize VAD
      const vad = new VoiceActivityDetector({
        energyThreshold: 0.02,
        speechStartFrames: 3,
        speechEndFrames: 10,
      });

      vadRef.current = vad;

      await vad.connect(stream);

      vad.start({
        onSpeechStart: () => {
          logger.debug('Speech started');
          setState((prev) => ({ ...prev, isSpeaking: true }));
        },
        onSpeechEnd: () => {
          logger.debug('Speech ended');
          setState((prev) => ({ ...prev, isSpeaking: false }));
        },
        onVolumeChange: (volume) => {
          setState((prev) => ({ ...prev, volume }));
        },
      });

      // Start recording
      mediaRecorder.start(100); // Collect data every 100ms

      startTimeRef.current = Date.now();

      // Update duration
      durationIntervalRef.current = window.setInterval(() => {
        const duration = (Date.now() - startTimeRef.current) / 1000;
        setState((prev) => ({ ...prev, duration }));
      }, 100);

      setState((prev) => ({
        ...prev,
        isRecording: true,
        error: null,
      }));

      logger.info('Voice recording started');
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to start recording';
      logger.error('Failed to start recording', error);

      setState((prev) => ({
        ...prev,
        error: errorMessage,
        isRecording: false,
      }));

      throw error;
    }
  }, []);

  const stopRecording = useCallback(async (): Promise<Blob | null> => {
    return new Promise((resolve) => {
      const mediaRecorder = mediaRecorderRef.current;

      if (!mediaRecorder || mediaRecorder.state === 'inactive') {
        resolve(null);
        return;
      }

      logger.info('Stopping voice recording...');

      mediaRecorder.onstop = () => {
        // Create audio blob
        const mimeType = mediaRecorder.mimeType || 'audio/webm';
        const audioBlob = new Blob(audioChunksRef.current, {
          type: mimeType,
        });

        logger.info('Voice recording stopped', {
          size: audioBlob.size,
          type: audioBlob.type,
        });

        // Cleanup
        cleanup();

        setState((prev) => ({
          ...prev,
          isRecording: false,
          isSpeaking: false,
          volume: 0,
          duration: 0,
        }));

        resolve(audioBlob);
      };

      mediaRecorder.stop();
    });
  }, []);

  const cancelRecording = useCallback(() => {
    logger.info('Cancelling voice recording');

    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }

    cleanup();

    setState({
      isRecording: false,
      isSpeaking: false,
      volume: 0,
      duration: 0,
      error: null,
    });
  }, []);

  const cleanup = useCallback(() => {
    // Stop VAD
    if (vadRef.current) {
      vadRef.current.destroy();
      vadRef.current = null;
    }

    // Stop media stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    // Clear duration interval
    if (durationIntervalRef.current) {
      clearInterval(durationIntervalRef.current);
      durationIntervalRef.current = null;
    }

    // Clear refs
    audioChunksRef.current = [];
    mediaRecorderRef.current = null;
  }, []);

  return {
    state,
    startRecording,
    stopRecording,
    cancelRecording,
  };
}
