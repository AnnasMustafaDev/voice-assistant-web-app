# 🚀 QUICK START - Voice Agent with Microphone Lifecycle Control

## What Was Fixed

The voice agent frontend now has **strict microphone lifecycle control**:
- ✅ Microphone only activates during user input
- ✅ Microphone automatically disabled during agent response (TTS)
- ✅ Hard microphone kill if WebSocket disconnects
- ✅ Backend message format corrected
- ✅ Async cache cleanup fixed

## Start the System

### Terminal 1 - Start Backend
```powershell
cd d:\Work\reception-voice-agent\backend
python main.py
```

**Expected Output:**
```
Starting server on 0.0.0.0:8000
WebSocket endpoint: /voice/stream
Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2 - Start Frontend
```powershell
cd d:\Work\reception-voice-agent\frontend
npm run dev
```

**Expected Output:**
```
VITE v7.3.0  ready in XXX ms
➜  Local:   http://localhost:5173/
```

### Browser
```
Open: http://localhost:5173
```

## The Flow

1. **Click "🎤 Record"** → Mic turns ON
2. **Speak** → AI listens and detects your speech
3. **Release button** → Utterance sent to backend
4. **Mic turns OFF automatically**
5. **Backend processes**: STT → LLM → TTS
6. **Agent responds**: Audio plays through speaker
7. **Mic stays OFF** (no echo/overlap)
8. **Ready for next**: Click Record again

## Important Rules

### ❌ Mic Will NOT Start If:
- Agent is currently speaking (status = "SPEAKING")
- WebSocket is disconnected
- User hasn't granted microphone permission

### ✅ Mic Will Automatically Stop When:
- User releases the Record button + 700ms silence detected
- Backend responds (automatic)
- WebSocket disconnects (hard kill)
- User clicks Stop button

### 🔒 Security Features:
- **No always-on recording** (must hold button)
- **Auto-stop during TTS** (prevents echo)
- **Hard kill on disconnect** (no orphaned mics)

## Testing Checklist

```
Quick Test (2 minutes):

1. Open browser → http://localhost:5173
   ✓ See "IDLE" status
   
2. Click "🎤 Record" button
   ✓ Status shows "Listening"
   ✓ Mic should be on
   
3. Say something like: "Hello, how are you?"
   ✓ See transcript appear
   
4. Release button
   ✓ Status changes to "Thinking"
   ✓ Mic turns off
   
5. Wait 3-5 seconds
   ✓ Status changes to "Speaking"
   ✓ Agent responds with audio
   
6. Try clicking Record while agent speaking
   ✓ Button shows error: "Wait for agent to finish speaking"
   ✓ Mic does NOT start
   
7. After agent finishes
   ✓ Status back to "IDLE"
   ✓ Can record again

✅ ALL TESTS PASS = System is working!
```

## Console Logs to Watch

### Frontend Console (Chrome DevTools)
```
[App] WebSocket connected
[App] Starting microphone - user pressing button
[Mic] VAD: SPEAKING detected
[Mic] VAD: SILENCE detected
[App] Utterance finalized: 2345ms
[WS] Sending audio: 5678 bytes
[App] Agent response received: "Hello there!"
```

### Backend Console (Terminal)
```
[INFO] Client connected: demo-tenant:receptionist-1
[INFO] Received audio utterance: 5678 bytes
[INFO] STT: "Hello, how are you?"
[INFO] Generating response...
[INFO] Sending response to client
```

## If Something Doesn't Work

### Mic won't start
- [ ] Check microphone permission in browser
- [ ] Check backend is running (`python main.py`)
- [ ] Check agentState is not "speaking"
- [ ] Refresh browser page

### Backend doesn't respond
- [ ] Check backend URL: `http://localhost:8000`
- [ ] Check backend logs for errors
- [ ] Check message format matches (should say "Received audio")
- [ ] Check network tab in DevTools

### TTS audio won't play
- [ ] Check browser volume is on
- [ ] Check speaker is connected
- [ ] Check browser hasn't muted audio
- [ ] Check backend generated response (logs)

### Mic keeps recording or won't stop
- [ ] Click Stop button explicitly
- [ ] Check logs show `[Mic] VAD: SILENCE detected`
- [ ] Try speaking more clearly with pauses
- [ ] Refresh page

## Key Files

| File | Purpose |
|------|---------|
| `frontend/src/App.tsx` | Microphone lifecycle control |
| `frontend/src/hooks/useMicrophone.ts` | VAD & audio capture |
| `frontend/src/hooks/useWebSocket.ts` | WebSocket connection |
| `backend/app/api/routes/voice.py` | Message handler |
| `backend/app/main.py` | FastAPI app setup |

## Architecture

```
┌─────────────┐
│   Browser   │
│  Frontend   │
│             │
│ Mic Control │
│ VAD Engine  │
│ WebSocket   │
└──────┬──────┘
       │ {type: "audio_utterance", audio: "...", duration_ms: XXX}
       │
       ├─────────────────────────────────────┬──────────────────────┐
       │                                     │                      │
       v                                     v                      v
    STT (Groq)                         LLM (LangGraph)         TTS (Backend)
    Transcribe                         Generate Response        Generate Audio
    
       │                                     │                      │
       └─────────────────────────────────────┴──────────────────────┘
       │
       v
    {event: "audio_response", data: "...", text: "..."}
    
       │
       v
┌──────────────┐
│   Backend    │
│  FastAPI +   │
│  WebSocket   │
└──────────────┘
```

## Environment Variables

### Frontend (.env or vite.config.ts)
```
VITE_BACKEND_URL=http://localhost:8000
VITE_TENANT_ID=demo-tenant
VITE_AGENT_ID=receptionist-1
VITE_AGENT_NAME=Reception Agent
```

### Backend (.env)
```
GROQ_API_KEY=your-groq-api-key
DATABASE_URL=sqlite:///./app.db
ENVIRONMENT=development
```

## Common Commands

```powershell
# Backend
cd backend
python main.py                    # Start backend
python test_agent.py             # Test agent
python debug_groq.py            # Test Groq API

# Frontend
cd frontend
npm run dev                       # Start dev server
npm run build                     # Build for production
npm run preview                   # Preview production build
npm run lint                      # Check TypeScript
```

## Troubleshooting Commands

```powershell
# Check if backend is running
curl http://localhost:8000/health

# Check if frontend is running
curl http://localhost:5173

# View backend logs
cd backend && python main.py 2>&1 | tee logs.txt

# Clean rebuild frontend
cd frontend
rm -r node_modules
rm package-lock.json
npm install
npm run build
```

## Architecture Summary

**Microphone Lifecycle:**
```
IDLE → [User presses Record]
LISTENING → [User speaks]
LISTENING → [User releases / 700ms silence]
THINKING → [Send to backend]
SPEAKING → [Agent responds]
IDLE → [Ready for next]
```

**State Transitions:**
```
idle → listening: User action only
listening → thinking: Utterance finalized
thinking → speaking: Backend responds
speaking → idle: TTS complete
```

**Microphone Rules:**
```
✓ ON: During "listening" state only
✓ OFF: After utterance finalized
✓ OFF: During "speaking" state (agent TTS)
✓ BLOCKED: Cannot start if state = "speaking"
✓ KILLED: If WebSocket disconnects
```

## Success Indicators

✅ **System is working if:**
- Record button responsive
- Mic indicator shows on/off correctly
- Transcription appears as you speak
- Backend responds with agent audio
- Mic disabled during agent response
- No console errors

❌ **System has issues if:**
- Record button unresponsive
- Mic stays on after utterance
- No backend response
- Backend doesn't receive audio
- Agent response won't play
- Lots of console errors

## Performance Tips

- **Latency**: Expect 2-5 seconds total (STT + LLM + TTS)
- **Audio Quality**: 16kHz 16-bit PCM (optimized for Groq)
- **Rate Limit**: 10 utterances per minute (rate limiting on WebSocket)
- **Silent Wait**: No timeout, can sit in idle indefinitely

## Support

For issues:
1. Check console logs (`[App]`, `[Mic]`, `[WS]` prefixes)
2. Check backend logs for errors
3. Verify all services running
4. Try refreshing browser
5. Check microphone permissions

---

**Ready to test!** Open http://localhost:5173 and try speaking to the voice agent.
