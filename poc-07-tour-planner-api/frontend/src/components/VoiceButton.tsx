/**
 * VoiceButton Component
 * Button for voice recording with visual feedback
 */

import React, { useEffect, useState } from 'react';
import { useVoiceRecorder } from '@/hooks/useVoiceRecorder';
import { useVoiceChat } from '@/hooks/useVoiceChat';
import { logger } from '@/utils/logger';

interface VoiceButtonProps {
  userId: string;
  sessionId?: string;
  voice?: string;
  onTranscription?: (text: string) => void;
  disabled?: boolean;
}

export const VoiceButton: React.FC<VoiceButtonProps> = ({
  userId,
  sessionId,
  voice = 'alloy',
  onTranscription,
  disabled = false,
}) => {
  const [isHolding, setIsHolding] = useState(false);

  const voiceRecorder = useVoiceRecorder();
  const voiceChat = useVoiceChat({
    userId,
    sessionId,
    voice,
    onTranscription,
  });

  const { state: recorderState } = voiceRecorder;
  const { state: chatState } = voiceChat;

  // Handle recording stop automatically after 30 seconds
  useEffect(() => {
    if (recorderState.isRecording && recorderState.duration >= 30) {
      handleStopRecording();
    }
  }, [recorderState.isRecording, recorderState.duration]);

  const handleMouseDown = () => {
    if (disabled || chatState.isProcessing) return;
    setIsHolding(true);
    startRecording();
  };

  const handleMouseUp = () => {
    if (!isHolding) return;
    setIsHolding(false);
    handleStopRecording();
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    e.preventDefault();
    handleMouseDown();
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    e.preventDefault();
    handleMouseUp();
  };

  const startRecording = async () => {
    try {
      await voiceRecorder.startRecording();
      logger.info('Voice recording started');
    } catch (error) {
      logger.error('Failed to start recording', error);
    }
  };

  const handleStopRecording = async () => {
    try {
      const audioBlob = await voiceRecorder.stopRecording();

      if (audioBlob && audioBlob.size > 0) {
        logger.info('Sending voice message', { size: audioBlob.size });
        await voiceChat.sendVoiceMessage(audioBlob);
      } else {
        logger.warn('No audio recorded');
      }
    } catch (error) {
      logger.error('Failed to process voice message', error);
    }
  };

  const getButtonState = () => {
    if (chatState.isProcessing) return 'processing';
    if (chatState.isPlayingAudio) return 'playing';
    if (recorderState.isRecording) {
      if (recorderState.isSpeaking) return 'speaking';
      return 'listening';
    }
    return 'idle';
  };

  const buttonState = getButtonState();
  const isActive = recorderState.isRecording || chatState.isProcessing || chatState.isPlayingAudio;

  return (
    <div className="voice-button-container">
      <button
        className={`voice-button voice-button-${buttonState}`}
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
        disabled={disabled || chatState.isProcessing}
        aria-label="Press and hold to speak"
      >
        {/* Microphone Icon */}
        <svg
          className="voice-icon"
          width="32"
          height="32"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M12 1C10.34 1 9 2.34 9 4V12C9 13.66 10.34 15 12 15C13.66 15 15 13.66 15 12V4C15 2.34 13.66 1 12 1Z"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            fill={isActive ? 'currentColor' : 'none'}
          />
          <path
            d="M19 10V12C19 15.866 15.866 19 12 19C8.134 19 5 15.866 5 12V10"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M12 19V23M8 23H16"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>

        {/* Volume indicator */}
        {recorderState.isRecording && (
          <div className="volume-indicator">
            {Array.from({ length: 5 }).map((_, i) => (
              <div
                key={i}
                className="volume-bar"
                style={{
                  opacity: recorderState.volume * 20 > i ? 1 : 0.3,
                }}
              />
            ))}
          </div>
        )}

        {/* Pulsing animation */}
        {isActive && <div className="voice-pulse" />}
      </button>

      {/* Status text */}
      <div className="voice-status">
        {buttonState === 'idle' && <span>Hold to speak</span>}
        {buttonState === 'listening' && (
          <span>
            Listening... {Math.floor(recorderState.duration)}s
          </span>
        )}
        {buttonState === 'speaking' && (
          <span className="voice-speaking">
            Speaking... {Math.floor(recorderState.duration)}s
          </span>
        )}
        {buttonState === 'processing' && <span>Processing...</span>}
        {buttonState === 'playing' && <span>Agent speaking...</span>}
      </div>

      {/* Transcription display */}
      {chatState.transcribedText && (
        <div className="voice-transcription">
          <span className="transcription-label">You said:</span>
          <span className="transcription-text">{chatState.transcribedText}</span>
        </div>
      )}

      {/* Error display */}
      {(recorderState.error || chatState.error) && (
        <div className="voice-error">
          {recorderState.error || chatState.error}
        </div>
      )}
    </div>
  );
};
