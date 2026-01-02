# Quick Reference Card

## 🚀 Get Started (5 minutes)

```bash
# 1. Configure
cd backend
cat > .env << EOF
GROQ_API_KEY=gsk_your_key_here
DEEPGRAM_API_KEY=your_key_here
EOF

# 2. Install
pip install -r requirements.txt

# 3. Run
python -m uvicorn app.main:app --reload

# 4. Test
curl http://localhost:8000/health
# {"status": "ok", "version": "2.0.0"}
```

---

## 📡 WebSocket Protocol

### Send Audio
```json
{"event": "audio", "audio": "base64_pcm", "latency_ms": 45}
```

### Receive Events
```
ready → user_transcript → assistant_transcript → audio... → audio_complete
```

---

## 🛠️ Tools Available

| Tool | Call When | Example |
|------|-----------|---------|
| `get_business_info` | "What are your hours?" | `topic="hours"` |
| `place_order` | "I want 2 burgers" | `customer_name, item, quantity` |
| `lookup_order` | "Status of order 123?" | `order_id="ORD-00001"` |

---

## 📁 File Structure

```
backend/app/
├── main.py           # FastAPI + /ws/voice
├── voice_agent.py    # WebSocket loop (core)
├── stt.py           # Deepgram
├── llm_client.py    # Groq + tools
├── tts.py           # Speech synthesis
├── tools.py         # Tool registry
└── config.py        # Settings
```

---

## 🎯 Add New Tool (2 steps)

```python
# 1. In app/tools.py
def my_tool(param: str) -> dict:
    return {"result": "..."}

# 2. Register
TOOLS["my_tool"] = Tool(
    name="my_tool",
    description="...",
    parameters=[...],
    func=my_tool
)
```

Done! LLM has access.

---

## 🐛 Debug

```bash
# Enable debug logging
DEBUG=true python -m uvicorn app.main:app --reload

# Check latency_ms field in WebSocket messages
# Measure from client (milliseconds since last event)

# View tool calls in console output
```

---

## 📊 Performance

- **STT Latency**: ~50-100ms (Deepgram)
- **LLM Latency**: ~200-500ms (Groq)
- **TTS Latency**: ~100-200ms
- **Total**: ~500-1000ms per turn

---

## 🔐 Configuration

| Variable | Required | Default |
|----------|----------|---------|
| `GROQ_API_KEY` | ✅ | - |
| `DEEPGRAM_API_KEY` | ✅ | - |
| `LLM_MODEL` | ❌ | `mixtral-8x7b-32768` |
| `TTS_PROVIDER` | ❌ | `groq` |
| `DATA_DIR` | ❌ | `./data` |
| `VOICE_TIMEOUT` | ❌ | `30` |
| `DEBUG` | ❌ | `false` |

---

## 🎬 Frontend Connection

```typescript
const url = "ws://localhost:8000/ws/voice";
const ws = new WebSocket(url);

ws.onopen = () => {
  ws.send(JSON.stringify({
    event: "audio",
    audio: "base64_pcm_chunk",
    latency_ms: 45
  }));
};

ws.onmessage = (e) => {
  const msg = JSON.parse(e.data);
  // Handle msg.event: ready, user_transcript, audio, etc.
};
```

---

## 📚 Documentation

| Doc | Purpose |
|-----|---------|
| `backend/README_NEW.md` | Full API reference |
| `IMPLEMENTATION_COMPLETE.md` | Architecture deep dive |
| `REFACTORING_SUMMARY.md` | What changed |

---

## ✅ Status

- Backend: ✅ Complete & tested
- Frontend: ✅ Updated & compatible
- Docs: ✅ Comprehensive
- Ready: ✅ For testing & deployment

---

## 🆘 Troubleshooting

| Issue | Fix |
|-------|-----|
| WebSocket refused | Check backend running on :8000 |
| Invalid API key | Verify `GROQ_API_KEY` and `DEEPGRAM_API_KEY` |
| No audio | Check audio format is MP3 |
| Tool not found | Verify tool name in `TOOLS` dict |
| Timeout | Increase `VOICE_TIMEOUT` or check network |

---

## 🚀 Deploy

```bash
# Docker
docker build -t voice-agent .
docker run -p 8000:8000 \
  -e GROQ_API_KEY=your_key \
  -e DEEPGRAM_API_KEY=your_key \
  voice-agent
```

---

**Built:** January 2, 2026
**Version:** 2.0.0
**Status:** Production Ready ✅
