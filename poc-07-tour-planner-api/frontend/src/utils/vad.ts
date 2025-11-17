/**
 * Voice Activity Detection (VAD) Utility
 * Detects when user is speaking based on audio analysis
 */

export interface VADConfig {
  /** Minimum RMS energy to consider as speech */
  energyThreshold: number;
  /** Number of consecutive frames to confirm speech start */
  speechStartFrames: number;
  /** Number of consecutive frames to confirm speech end */
  speechEndFrames: number;
  /** Sample rate for analysis */
  sampleRate: number;
  /** FFT size for frequency analysis */
  fftSize: number;
}

export interface VADState {
  isSpeaking: boolean;
  energy: number;
  speechDuration: number;
}

export class VoiceActivityDetector {
  private audioContext: AudioContext;
  private analyser: AnalyserNode;
  private dataArray: Uint8Array;
  private config: VADConfig;

  private isSpeaking: boolean = false;
  private speechStartCount: number = 0;
  private speechEndCount: number = 0;
  private speechStartTime: number = 0;

  private onSpeechStart?: () => void;
  private onSpeechEnd?: () => void;
  private onVolumeChange?: (volume: number) => void;

  constructor(config: Partial<VADConfig> = {}) {
    this.config = {
      energyThreshold: 0.02, // Adjust based on testing
      speechStartFrames: 3,
      speechEndFrames: 10,
      sampleRate: 16000,
      fftSize: 2048,
      ...config,
    };

    this.audioContext = new AudioContext({ sampleRate: this.config.sampleRate });
    this.analyser = this.audioContext.createAnalyser();
    this.analyser.fftSize = this.config.fftSize;
    this.analyser.smoothingTimeConstant = 0.8;

    const bufferLength = this.analyser.frequencyBinCount;
    this.dataArray = new Uint8Array(bufferLength);
  }

  /**
   * Connect media stream to VAD
   */
  async connect(stream: MediaStream): Promise<void> {
    const source = this.audioContext.createMediaStreamSource(stream);
    source.connect(this.analyser);
  }

  /**
   * Start VAD analysis
   */
  start(callbacks: {
    onSpeechStart?: () => void;
    onSpeechEnd?: () => void;
    onVolumeChange?: (volume: number) => void;
  }): void {
    this.onSpeechStart = callbacks.onSpeechStart;
    this.onSpeechEnd = callbacks.onSpeechEnd;
    this.onVolumeChange = callbacks.onVolumeChange;

    this.analyze();
  }

  /**
   * Stop VAD analysis
   */
  stop(): void {
    this.onSpeechStart = undefined;
    this.onSpeechEnd = undefined;
    this.onVolumeChange = undefined;
  }

  /**
   * Analyze audio in real-time
   */
  private analyze(): void {
    if (!this.onSpeechStart && !this.onSpeechEnd && !this.onVolumeChange) {
      return; // Stopped
    }

    this.analyser.getByteTimeDomainData(this.dataArray);

    // Calculate RMS energy
    const energy = this.calculateRMS(this.dataArray);

    // Notify volume change
    if (this.onVolumeChange) {
      this.onVolumeChange(energy);
    }

    // Detect speech activity
    if (energy > this.config.energyThreshold) {
      // Potential speech detected
      this.speechStartCount++;
      this.speechEndCount = 0;

      if (
        !this.isSpeaking &&
        this.speechStartCount >= this.config.speechStartFrames
      ) {
        // Confirmed speech start
        this.isSpeaking = true;
        this.speechStartTime = Date.now();
        if (this.onSpeechStart) {
          this.onSpeechStart();
        }
      }
    } else {
      // Silence detected
      this.speechStartCount = 0;

      if (this.isSpeaking) {
        this.speechEndCount++;

        if (this.speechEndCount >= this.config.speechEndFrames) {
          // Confirmed speech end
          this.isSpeaking = false;
          this.speechEndCount = 0;
          if (this.onSpeechEnd) {
            this.onSpeechEnd();
          }
        }
      }
    }

    // Continue analysis
    requestAnimationFrame(() => this.analyze());
  }

  /**
   * Calculate RMS (Root Mean Square) energy
   */
  private calculateRMS(data: Uint8Array): number {
    let sum = 0;
    for (let i = 0; i < data.length; i++) {
      const normalized = (data[i] - 128) / 128;
      sum += normalized * normalized;
    }
    return Math.sqrt(sum / data.length);
  }

  /**
   * Get current VAD state
   */
  getState(): VADState {
    const speechDuration = this.isSpeaking
      ? Date.now() - this.speechStartTime
      : 0;

    return {
      isSpeaking: this.isSpeaking,
      energy: 0, // Would need to store from last analysis
      speechDuration,
    };
  }

  /**
   * Clean up resources
   */
  destroy(): void {
    this.stop();
    if (this.audioContext.state !== 'closed') {
      this.audioContext.close();
    }
  }
}
