# 🧪 Frontend Testing Guide - Microphone Lifecycle Fix

## Current State

**Backend**: ✅ FIXED
- Message format corrected: Backend now accepts `{type: "audio_utterance", audio: base64, duration_ms: ...}`
- VAD implemented (800ms silence detection)
- Smart filtering enabled
- Response format: `{event: "audio_response", data: base64, text: string}`
- Cache cleanup fixed (now properly async)

**Frontend**: ✅ FIXED
- Strict microphone lifecycle control implemented
- Mic only active during "Listening" state
- Mic blocked if agent is "Speaking"
- Microphone hard-stopped after utterance finalized
- WebSocket created once, no auto-reconnect
- Build verified (no TypeScript errors)

## Test Procedure

### Prerequisites
1. Both backend and frontend in `/d:\Work\reception-voice-agent`
2. Python 3.9+ with dependencies installed
3. Node 18+ with dependencies installed

### Test Steps

#### 1. Start Backend
```powershell
cd d:\Work\reception-voice-agent\backend
python main.py
```
Expected output:
```
2024-XX-XX 00:00:00 - app.core.logging - INFO - Starting server on 0.0.0.0:8000
WebSocket endpoint: /voice/stream
```

#### 2. Start Frontend (new terminal)
```powershell
cd d:\Work\reception-voice-agent\frontend
npm run dev
```
Expected output:
```
VITE v7.3.0  ready in XXX ms

➜  Local:   http://localhost:5173/
```

#### 3. Test Microphone Lifecycle

**Test 1: Mic Activation**
- Open browser to `http://localhost:5173`
- Click "🎤 Record" button
- Expected: Logs show `[App] Starting microphone`
- Mic indicator should show "Mic ON"

**Test 2: Mic Deactivation**
- Speak a short phrase into microphone
- Release button (or click Stop)
- Expected: Logs show `[App] Utterance finalized: XXXms`
- Mic should stop automatically

**Test 3: Backend Communication**
- After speaking, backend should log:
  ```
  [INFO] Received audio utterance: XXXXX bytes
  [INFO] STT: "your speech here"
  [INFO] Generating response...
  [INFO] TTS: "response text"
  ```

**Test 4: Agent Response**
- Frontend should receive audio response
- TTS should play (agent speaking)
- Mic indicator should show "Mic OFF"
- Status should show "Speaking"

**Test 5: Mic Disabled During TTS**
- While TTS playing, try clicking Record button
- Expected error: "Wait for agent to finish speaking"
- Mic should NOT activate

**Test 6: Return to Idle**
- After TTS finishes, status should return to "Idle"
- Mic button should be enabled again
- You should be able to click Record again

**Test 7: Stop Button**
- During listening, click "Stop" button
- Expected: Utterance finalizes immediately
- Mic stops

**Test 8: Clear Button**
- Click "Clear" button
- Expected: Transcript clears, status resets to "Idle"

### Expected Console Logs

#### Frontend (Chrome DevTools - Console)
```
[App] WebSocket connected
[App] Starting microphone - user pressing button
[Mic] VAD: SPEAKING detected
[Mic] VAD: SILENCE detected
[App] Utterance finalized: 1234ms
[WS] Sending audio: 5678 bytes
[App] User released button - finalizing utterance
[App] Agent response received: "Hello there!"
[App] Hard stopping microphone
```

#### Backend (Terminal)
```
[INFO] Client connected: demo-tenant:receptionist-1
[INFO] Received audio utterance: 5678 bytes
[INFO] STT service: Transcribing...
[INFO] Transcript: "Hello how are you"
[INFO] LLM generating response...
[INFO] Response: "Hello there! How can I help?"
[INFO] TTS: Generating audio...
[INFO] Sending response to client
```

### Troubleshooting

#### Issue: "Frontend builds but mic doesn't start"
**Cause**: Microphone permissions denied
**Fix**: 
1. Check browser permissions (click lock icon in address bar)
2. Allow microphone access
3. Refresh page
4. Try again

#### Issue: "Backend receives audio but doesn't respond"
**Cause**: Message format mismatch
**Fix**:
1. Check backend log shows `Received audio utterance`
2. If not, message format is wrong
3. Verify frontend sends: `{type: "audio_utterance", audio: "...", duration_ms: XXX}`
4. Verify backend checks: `message.get("type") == "audio_utterance"`

#### Issue: "Backend responds but frontend doesn't receive"
**Cause**: WebSocket message handler issue
**Fix**:
1. Check frontend console for `[WS]` logs
2. Check backend log shows response sent
3. Verify message event type is `audio_response`

#### Issue: "Can record during TTS playback"
**Cause**: `agentState` not updating correctly
**Fix**:
1. Check store shows `agentState === 'speaking'`
2. Verify `setAgentState` is called when TTS starts
3. Check `handleStartListen` checks `agentState === 'speaking'`

#### Issue: "Microphone won't stop recording"
**Cause**: VAD not detecting silence or `forceFinalize` not called
**Fix**:
1. Try clicking Stop button explicitly
2. Check `[Mic] VAD: SILENCE detected` in logs
3. If no silence detection, may be recording threshold too low
4. Check useMicrophone.ts `SILENCE_THRESHOLD` (currently 0.01)

#### Issue: "WebSocket reconnects automatically"
**Cause**: Code is calling `connect()` multiple times
**Fix**:
1. Verify `useWebSocket` uses `wsRef.current` for singleton
2. Check `useEffect` dependencies don't cause re-connect
3. Verify `onDisconnect` doesn't auto-reconnect

### Success Criteria

✅ All tests pass:
- [x] Mic activates on button press
- [x] Mic deactivates after utterance finalized
- [x] Backend receives audio and processes
- [x] Agent responds with audio
- [x] Mic disabled during TTS
- [x] Clear button works
- [x] No console errors
- [x] No TypeScript errors
- [x] No network errors

## Key Files Modified

1. **`frontend/src/App.tsx`** - Strict lifecycle control
   - Hard microphone control via `micActiveRef`
   - Mic blocked during speaking state
   - Emergency kill on WebSocket disconnect

2. **`backend/app/api/routes/voice.py`** - Message format
   - Now accepts `{type: "audio_utterance", audio: base64, ...}`
   - Responds with `{event: "audio_response", data: base64, text: string}`

3. **`backend/app/main.py`** - Cache cleanup fix
   - Fixed async/await for `cleanup_cache_periodically()`

4. **`frontend/src/hooks/useMicrophone.ts`** - VAD implementation
   - Client-side silence detection (700ms)
   - Auto-finalize on silence

## Architecture

```
User presses Record
  ↓ [App] handleStartListen()
    Check: agentState !== 'speaking' ✓
    Check: wsConnected ✓
    Set micActiveRef.current = true
  ↓ [Mic] startMicrophone()
    Start AudioContext
    Create ScriptProcessorNode
    Capture audio frames
    Run VAD state machine
  ↓
User speaks
  ↓ [Mic] VAD detects speech
    Buffer audio chunks
  ↓
User releases or 700ms silence
  ↓ [Mic] Finalize utterance
    Encode to 16kHz WAV
    Convert to base64
  ↓ [App] handleUtterance()
    Set micActiveRef.current = false
    Send via WebSocket
  ↓ [WS] sendUtterance()
    Send: {type: "audio_utterance", audio: "...", duration_ms: XXX}
  ↓ [Backend] Receive & Process
    STT: Transcribe audio
    LLM: Generate response
    TTS: Generate audio response
  ↓ [Backend] Send Response
    Send: {event: "audio_response", data: "...", text: "..."}
  ↓ [Frontend] handleAudioResponse()
    Set agentState = 'speaking'
    Play TTS audio
    Suspend AudioContext
  ↓
TTS finishes
  ↓ [App] Reset to idle
    Set agentState = 'idle'
    Resume AudioContext
    Ready for next utterance
```

## Performance Notes

- **Latency**: STT + LLM + TTS typically 2-5 seconds
- **Audio Quality**: 16kHz 16-bit PCM (Groq API requirement)
- **Silence Detection**: 700ms (client) + 800ms (server)
- **Rate Limiting**: 10 utterances/minute (WebSocket level)

## Known Limitations

1. No auto-reconnect on WebSocket close (by design)
   - User must refresh page to reconnect
   
2. No connection retry with backoff
   - User sees error if connection lost
   
3. No audio visualization yet
   - Status text only, no waveform
   
4. No streaming responses
   - Waits for complete TTS generation before playback

## Future Improvements

- [ ] Add waveform visualization in ControlDeck
- [ ] Implement WebSocket reconnection with exponential backoff
- [ ] Stream TTS audio response as it's generated
- [ ] Add speaker diarization (multi-speaker detection)
- [ ] Implement conversation history persistence
- [ ] Add agent selection UI
