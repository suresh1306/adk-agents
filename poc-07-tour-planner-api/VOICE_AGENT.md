# Voice Agent Guide for Tour Planner

Complete guide to the intelligent voice agent capabilities in the Tour Planner application.

## Overview

The Tour Planner now features a fully integrated voice agent with:
- **Speech-to-Text**: Groq Whisper large-v3-turbo for accurate transcription
- **Text-to-Speech**: Groq PlayAI TTS with natural-sounding voices
- **Voice Activity Detection (VAD)**: Intelligent detection of speech start/end
- **Real-time Processing**: Streaming audio responses
- **Human-like Interaction**: Natural conversation flow with visual feedback

## Features

### 🎤 Voice Input
- **Push-to-Talk**: Hold the microphone button to speak
- **Automatic Speech Detection**: VAD detects when you start and stop speaking
- **Visual Feedback**: Real-time volume indicators and status updates
- **30-Second Limit**: Automatic stop after 30 seconds (configurable)
- **High-Quality Recording**: 16kHz sample rate with noise suppression

### 🔊 Voice Output
- **Natural Voices**: Choose from 23+ different Groq PlayAI TTS voices
- **Streaming Audio**: Immediate playback as audio is received
- **Female Voice Options**:
  - `Jennifer-PlayAI` - Professional, clear (default)
  - `Celeste-PlayAI` - Warm, friendly
  - `Eleanor-PlayAI` - Sophisticated
  - `Arista-PlayAI` - Clear, articulate
  - `Adelaide-PlayAI` - Mature, professional
  - `Aaliyah-PlayAI` - Young, energetic
  - `Cheyenne-PlayAI` - Expressive
  - `Gail-PlayAI` - Confident
  - `Indigo-PlayAI` - Modern
  - `Judy-PlayAI` - Cheerful
  - `Deedee-PlayAI` - Playful
  - `Mamaw-PlayAI` - Grandmother-like
- **Male Voice Options**:
  - `Atlas-PlayAI` - Strong, authoritative
  - `Briggs-PlayAI` - Professional
  - `Calum-PlayAI` - Friendly
  - `Cillian-PlayAI` - Warm
  - `Basil-PlayAI` - Mature
  - `Angelo-PlayAI` - Young
  - `Chip-PlayAI` - Energetic
  - `Fritz-PlayAI` - Distinctive
  - `Mason-PlayAI` - Casual
  - `Mikail-PlayAI` - Sophisticated
  - `Mitch-PlayAI` - Conversational

### 🎯 Intelligent Features
- **Context Awareness**: Maintains conversation context across interactions
- **Session Management**: Voice messages tied to chat sessions
- **Dual Input**: Seamlessly switch between voice and text
- **Error Handling**: Graceful fallback with helpful error messages
- **Accessibility**: Full keyboard navigation and ARIA labels

## Architecture

### Backend Components

#### 1. Voice Service (`voice_service.py`)
Core service handling all voice operations:

```python
class VoiceAgentService:
    - transcribe_audio(): STT using Groq Whisper
    - synthesize_speech(): TTS using Groq PlayAI
    - synthesize_speech_streaming(): Streaming TTS
    - process_voice_message(): End-to-end voice processing
```

#### 2. API Endpoints

**Transcribe Audio**
```http
POST /api/voice/transcribe
Content-Type: multipart/form-data

audio: <audio file>
```

**Synthesize Speech**
```http
POST /api/voice/synthesize
{
  "text": "Hello, how can I help you?",
  "voice": "Jennifer-PlayAI",
  "model": "playai-tts"
}
```

**Voice Chat (Full Conversation)**
```http
POST /api/voice/chat
Content-Type: multipart/form-data

audio: <audio file>
user_id: user_123
session_id: session_abc (optional)
voice: alloy (optional)
```

### Frontend Components

#### 1. Voice Activity Detection (`utils/vad.ts`)
Real-time speech detection:

```typescript
class VoiceActivityDetector:
  - RMS energy calculation
  - Speech start/end detection
  - Configurable thresholds
  - Volume level monitoring
```

**Configuration:**
```typescript
{
  energyThreshold: 0.02,        // Sensitivity threshold
  speechStartFrames: 3,         // Frames to confirm speech start
  speechEndFrames: 10,          // Frames to confirm speech end
  sampleRate: 16000,            // Audio sample rate
  fftSize: 2048                 // FFT size for analysis
}
```

#### 2. Voice Recorder Hook (`hooks/useVoiceRecorder.ts`)
Manages audio recording with VAD:

```typescript
const { state, startRecording, stopRecording, cancelRecording } = useVoiceRecorder();

state: {
  isRecording: boolean,
  isSpeaking: boolean,
  volume: number,
  duration: number,
  error: string | null
}
```

#### 3. Voice Chat Hook (`hooks/useVoiceChat.ts`)
Integrates with backend API:

```typescript
const { state, sendVoiceMessage, stopAudio, clearError } = useVoiceChat({
  userId,
  sessionId,
  voice,
  onTranscription
});
```

#### 4. Voice Button Component (`components/VoiceButton.tsx`)
Complete UI component with visual feedback:

- Push-to-talk interaction
- Real-time status display
- Volume visualization
- Error handling
- Transcription display

## Setup

### 1. Backend Setup

**Install Dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

**Configure Environment:**
```bash
cp .env.example .env
```

Edit `.env` with your API keys:
```env
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key
```

**⚠️ Accept Groq PlayAI TTS Terms (REQUIRED):**

Before using voice features, you must accept the PlayAI TTS terms:

1. Visit: https://console.groq.com/playground?model=playai-tts
2. Sign in with your Groq account
3. Accept the model terms when prompted
4. Wait a moment for the acceptance to propagate

**Start Server:**
```bash
uvicorn api_server:app --reload --port 8000
```

### 2. Frontend Setup

**Install Dependencies:**
```bash
cd frontend
npm install
```

**Start Development Server:**
```bash
npm run dev
```

### 3. Browser Permissions

The voice agent requires microphone access. When you first click the voice button:
1. Browser will prompt for microphone permission
2. Click "Allow" to enable voice features
3. Permission is remembered for future sessions

## Usage

### Basic Voice Interaction

1. **Start Speaking**:
   - Click and hold the microphone button
   - Start speaking when you see "Listening..."
   - Voice activity indicator shows when speech is detected

2. **Stop Recording**:
   - Release the button when done
   - Audio automatically processes
   - Status shows "Processing..."

3. **Receive Response**:
   - Transcription appears briefly
   - Agent processes your message
   - Audio response plays automatically
   - Status shows "Agent speaking..."

### Advanced Features

#### Custom Voice Selection

In `ChatPage.tsx`:
```typescript
<VoiceButton
  userId={userId}
  sessionId={currentSession?.session_id}
  voice="nova"  // Change voice here
  onTranscription={(text) => sendMessage(text)}
/>
```

#### Adjust VAD Sensitivity

In `useVoiceRecorder.ts`:
```typescript
const vad = new VoiceActivityDetector({
  energyThreshold: 0.03,  // Higher = less sensitive
  speechStartFrames: 5,   // More frames = slower start
  speechEndFrames: 15,    // More frames = longer silence needed
});
```

#### Handle Transcription

```typescript
<VoiceButton
  onTranscription={(text) => {
    console.log('User said:', text);
    // Custom handling
  }}
/>
```

## Audio Formats

### Input (Recording)
- **Format**: WebM with Opus codec (fallback to WebM)
- **Sample Rate**: 16kHz
- **Channels**: Mono
- **Features**: Echo cancellation, noise suppression, auto gain

### Output (TTS)
- **Format**: MP3
- **Model**: Groq PlayAI TTS (playai-tts)
- **Streaming**: Chunked delivery for immediate playback

## Performance Optimization

### Backend
- Async/await throughout for non-blocking operations
- Streaming TTS for faster response times
- Connection pooling with httpx
- Efficient audio format conversion

### Frontend
- Web Audio API for low-latency playback
- Efficient VAD with requestAnimationFrame
- Optimized re-renders with React hooks
- Audio context reuse

## Error Handling

### Common Errors and Solutions

**Microphone Permission Denied**
```
Error: Permission denied
Solution: Allow microphone access in browser settings
```

**No Speech Detected**
```
Error: No speech detected in audio
Solution: Speak louder or adjust VAD threshold
```

**API Key Missing**
```
Error: GROQ_API_KEY is required
Solution: Add API keys to backend/.env file
```

**PlayAI TTS Terms Not Accepted**
```
Error: PlayAI TTS requires terms acceptance
Solution: Visit https://console.groq.com/playground?model=playai-tts
         and accept the terms, then restart the server
```

**Network Error**
```
Error: Failed to connect to server
Solution: Ensure backend is running on port 8000
```

### Error Recovery

The voice agent includes automatic error recovery:
- Failed recordings can be retried immediately
- Network errors show user-friendly messages
- Graceful degradation if voice features unavailable
- Fallback to text input always available

## Voice Activity Detection (VAD)

### How It Works

1. **Audio Analysis**: Captures audio and calculates RMS energy
2. **Threshold Comparison**: Compares energy to configured threshold
3. **Frame Counting**: Requires multiple consecutive frames to confirm
4. **Event Emission**: Triggers callbacks for speech start/end

### Tuning VAD

For **noisy environments**, increase threshold:
```typescript
energyThreshold: 0.05  // Less sensitive
speechEndFrames: 20    // Longer silence needed
```

For **quiet environments**, decrease threshold:
```typescript
energyThreshold: 0.01  // More sensitive
speechEndFrames: 8     // Shorter silence needed
```

### VAD Visualization

The UI shows real-time VAD status:
- **Volume bars**: Current audio level
- **Color changes**:
  - Yellow: Listening (no speech)
  - Green: Speaking detected
  - Purple: Processing
  - Blue: Agent responding

## API Reference

### Voice Service Methods

#### `transcribe_audio(audio_data, content_type)`
Transcribe audio to text using Groq Whisper.

**Parameters:**
- `audio_data` (bytes): Raw audio data
- `content_type` (str): MIME type (audio/webm, audio/wav, etc.)

**Returns:**
```python
AudioTranscription(
  text="transcribed text",
  language="en",
  duration=5.2
)
```

#### `synthesize_speech(text, voice, model)`
Convert text to speech using Groq PlayAI TTS.

**Parameters:**
- `text` (str): Text to synthesize
- `voice` (str): Voice name (alloy, echo, fable, onyx, nova, shimmer)
- `model` (str): Model name (playai-tts)

**Returns:**
- `bytes`: MP3 audio data

#### `synthesize_speech_streaming(text, voice, chunk_size)`
Stream synthesized speech in chunks.

**Parameters:**
- `text` (str): Text to synthesize
- `voice` (str): Voice name
- `chunk_size` (int): Chunk size in bytes (default: 4096)

**Yields:**
- Audio chunks as bytes

### Frontend Hooks

#### `useVoiceRecorder()`
Hook for voice recording with VAD.

**Returns:**
```typescript
{
  state: VoiceRecorderState,
  startRecording: () => Promise<void>,
  stopRecording: () => Promise<Blob | null>,
  cancelRecording: () => void
}
```

#### `useVoiceChat(options)`
Hook for voice chat integration.

**Parameters:**
```typescript
{
  userId: string,
  sessionId?: string,
  voice?: string,
  onTranscription?: (text: string) => void
}
```

**Returns:**
```typescript
{
  state: VoiceChatState,
  sendVoiceMessage: (audioBlob: Blob) => Promise<void>,
  stopAudio: () => void,
  clearError: () => void
}
```

## Security Considerations

### Backend
- ✅ Audio data validated before processing
- ✅ File size limits enforced
- ✅ API keys stored securely in environment variables
- ✅ CORS configured for trusted origins
- ✅ Rate limiting recommended for production

### Frontend
- ✅ Microphone access requires user permission
- ✅ Audio data encrypted in transit (HTTPS)
- ✅ Session IDs used for authorization
- ✅ Error messages don't expose sensitive data

## Testing

### Manual Testing

1. **Test Voice Recording**:
   ```
   - Click and hold mic button
   - Speak: "I want to visit Japan"
   - Release button
   - Verify transcription appears
   - Verify agent responds
   ```

2. **Test VAD**:
   ```
   - Start recording
   - Remain silent (should show "Listening")
   - Speak (should show "Speaking")
   - Stop speaking (should detect end)
   ```

3. **Test Error Handling**:
   ```
   - Deny microphone permission
   - Record with no speech
   - Test with network offline
   - Verify error messages
   ```

### API Testing

Using cURL:
```bash
# Test transcription
curl -X POST http://localhost:8000/api/voice/transcribe \
  -F "audio=@recording.webm"

# Test TTS
curl -X POST http://localhost:8000/api/voice/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello world","voice":"alloy"}' \
  --output speech.mp3

# Test voice chat
curl -X POST http://localhost:8000/api/voice/chat \
  -F "audio=@recording.webm" \
  -F "user_id=test_user" \
  -F "voice=alloy"
```

## Troubleshooting

### Issue: Voice button doesn't work

**Check:**
1. Microphone permission granted in browser
2. Backend server running on port 8000
3. API keys configured in backend/.env
4. Browser supports Web Audio API and MediaRecorder

**Solution:**
```bash
# Check backend logs
tail -f backend/logs/api.log

# Verify API keys
cat backend/.env | grep API_KEY

# Test microphone access
navigator.mediaDevices.getUserMedia({ audio: true })
```

### Issue: Poor transcription quality

**Possible Causes:**
- Background noise
- Low microphone volume
- Audio encoding issues

**Solutions:**
- Use a better microphone
- Adjust input volume
- Enable noise suppression in browser
- Use a quieter environment

### Issue: Slow response times

**Optimizations:**
- Groq PlayAI TTS is already optimized for speed
- Enable streaming TTS (already implemented)
- Increase network bandwidth
- Deploy backend closer to users

### Issue: VAD not detecting speech

**Adjust Settings:**
```typescript
// Lower threshold for more sensitivity
energyThreshold: 0.01

// Fewer frames to start faster
speechStartFrames: 2

// Longer silence for slower cutoff
speechEndFrames: 15
```

## Future Enhancements

- [ ] Interrupt agent while speaking
- [ ] Voice activity visualization waveform
- [ ] Multi-language support
- [ ] Custom wake word detection
- [ ] Voice command shortcuts
- [ ] Offline voice processing
- [ ] Voice biometric authentication
- [ ] Emotion detection in voice
- [ ] Background noise filtering
- [ ] Echo cancellation improvements

## Resources

- **Groq API (Whisper & PlayAI TTS)**: https://groq.com/
- **Groq API Documentation**: https://console.groq.com/docs/
- **Web Audio API**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API
- **MediaRecorder API**: https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder

## Support

For issues or questions about the voice agent:
1. Check this documentation
2. Review backend logs
3. Test with example audio files
4. Check browser console for errors
5. Verify API keys and permissions

## License

MIT
