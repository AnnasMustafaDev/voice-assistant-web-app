# AI Voice Receptionist Backend

A minimal, fast, real-time AI receptionist backend built with FastAPI, Deepgram STT, and Groq LLM.

## Architecture

```
Client (WebSocket) 
  ↓
FastAPI /ws/voice
  ├→ Audio Stream (base64 PCM)
  │   ↓
  │ DeepgramSTT (real-time transcription)
  │   ↓
  │ LLMClient (with tool calling)
  │   ├→ [Tool Execution]
  │   │   ├ get_business_info()
  │   │   ├ place_order()
  │   │   └ lookup_order()
  │   ↓
  │ TTS (Groq/Deepgram)
  │   ↓
  │ Audio Response (base64 MP3)
  └→ Client
```

## Quick Start

### Prerequisites

- Python 3.11+
- Groq API key
- Deepgram API key

### Installation

```bash
# Clone repo
cd backend

# Create .env
cat > .env << EOF
GROQ_API_KEY=your_groq_key
DEEPGRAM_API_KEY=your_deepgram_key
LLM_MODEL=mixtral-8x7b-32768
TTS_PROVIDER=groq
DATA_DIR=./data
DEBUG=false
EOF

# Install dependencies
pip install -r requirements.txt

# Create data directory
mkdir -p data
cp data/business_data.json data/  # Or create your own
```

### Run Server

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Server will be available at: `ws://localhost:8000/ws/voice`

Health check: `http://localhost:8000/health`

## WebSocket Protocol

### Client → Server

```json
{
  "event": "audio",
  "audio": "base64_encoded_pcm_audio",
  "latency_ms": 45
}
```

Audio format:
- Encoding: PCM 16-bit signed
- Sample rate: 16kHz
- Channels: 1 (mono)
- Sent in chunks (e.g., 320ms of audio)

### Server → Client

#### Ready Signal
```json
{
  "event": "ready",
  "conversation_id": "session-1"
}
```

#### User Transcript
```json
{
  "event": "user_transcript",
  "text": "What are your hours?",
  "timestamp": 1672531200.0
}
```

#### Assistant Transcript
```json
{
  "event": "assistant_transcript",
  "text": "We're open 9am to 10pm daily.",
  "timestamp": 1672531201.0
}
```

#### Audio Response (streamed)
```json
{
  "event": "audio",
  "audio": "base64_encoded_mp3_audio",
  "chunk_num": 0,
  "timestamp": 1672531202.0
}
```

Multiple audio events may be sent for one response.

#### Audio Complete
```json
{
  "event": "audio_complete",
  "timestamp": 1672531203.0
}
```

#### Error
```json
{
  "event": "error",
  "message": "Error description"
}
```

## Tools

The LLM can call the following tools:

### get_business_info(topic: str)
Get information about the business.

**Topics:**
- `hours` - Business hours
- `location` - Physical address
- `menu` - Available menu items
- `pricing` - Item prices
- General info (returns all)

**Example:**
```
User: "What are your hours?"
LLM calls: get_business_info(topic="hours")
Response: {"hours": {"monday": "9am-10pm", ...}}
```

### place_order(customer_name: str, item: str, quantity: int)
Place a new order.

**Example:**
```
User: "I'd like to order 2 burgers"
LLM calls: place_order(customer_name="John", item="burger", quantity=2)
Response: {"success": true, "order_id": "ORD-00001"}
```

### lookup_order(order_id: str)
Look up an existing order.

**Example:**
```
User: "What's the status of order ORD-00001?"
LLM calls: lookup_order(order_id="ORD-00001")
Response: {"success": true, "order": {...}}
```

## Configuration

Edit `.env`:

```bash
# LLM Configuration
LLM_MODEL=mixtral-8x7b-32768  # Groq model
GROQ_API_KEY=your_key
DEEPGRAM_API_KEY=your_key

# Voice Configuration
SAMPLE_RATE=16000
CHANNELS=1
VOICE_TIMEOUT=30

# Storage
DATA_DIR=./data

# Server
DEBUG=false
```

## Business Data Format

`data/business_data.json`:

```json
{
  "name": "Restaurant Name",
  "location": "Address",
  "phone": "555-123-4567",
  "hours": {
    "monday": "9am-10pm",
    "tuesday": "9am-10pm"
  },
  "menu": [
    {
      "name": "burger",
      "description": "Description",
      "price": 12
    }
  ],
  "orders": []
}
```

## Performance

- **Latency**: ~100-200ms from user speech end to first LLM response
- **Throughput**: Multiple concurrent WebSocket connections
- **Audio encoding**: Real-time streaming with base64 encoding

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t voice-agent .
docker run -p 8000:8000 \
  -e GROQ_API_KEY=your_key \
  -e DEEPGRAM_API_KEY=your_key \
  voice-agent
```

### Environment Variables

- `GROQ_API_KEY` - Required
- `DEEPGRAM_API_KEY` - Required
- `LLM_MODEL` - Groq model (default: mixtral-8x7b-32768)
- `TTS_PROVIDER` - groq or deepgram (default: groq)
- `DATA_DIR` - Data storage directory (default: ./data)
- `DEBUG` - Enable debug logging (default: false)

## File Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app & routes
│   ├── config.py            # Configuration
│   ├── voice_agent.py       # WebSocket handler
│   ├── stt.py              # Deepgram STT
│   ├── llm_client.py       # Groq LLM with tools
│   ├── tts.py              # Text-to-speech
│   └── tools.py            # Tool definitions
├── data/
│   └── business_data.json  # Business information & orders
├── requirements.txt
├── main.py
└── .env
```

## Testing

Start the server and test with:

```bash
# Health check
curl http://localhost:8000/health

# WebSocket test (requires client - see frontend/)
# The frontend already handles this
```

## Frontend Integration

Frontend communicates via WebSocket at: `ws://localhost:8000/ws/voice`

See [../frontend/README.md](../frontend/README.md) for client setup.

## Development

### Adding New Tools

1. Add tool function in `app/tools.py`
2. Add to `TOOLS` registry
3. LLM will automatically have access to it

Example:

```python
def lookup_reservation(phone: str) -> dict:
    """Look up reservation by phone."""
    # Implementation
    pass

TOOLS["lookup_reservation"] = Tool(
    name="lookup_reservation",
    description="Look up a reservation",
    parameters=[...],
    func=lookup_reservation
)
```

### Debugging

Enable debug mode:

```bash
DEBUG=true python -m uvicorn app.main:app --reload
```

Check WebSocket messages in browser DevTools or client logs.

## Known Limitations

- Silence detection is simple (800ms threshold) - may need tuning
- Single audio stream per connection
- Tools store data in JSON (not suitable for high volume)
- No persistence across server restarts

## Next Steps

- Add database support (SQLite/PostgreSQL)
- Implement speaker verification
- Add conversation logging/analytics
- Multi-language support
- Advanced VAD (Voice Activity Detection)
- Streaming audio response with proper buffering
