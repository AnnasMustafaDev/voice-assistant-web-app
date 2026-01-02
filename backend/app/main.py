"""FastAPI application for AI voice receptionist."""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.voice_agent import VoiceAgent
from app.config import get_settings

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="AI Voice Receptionist",
    version="2.0.0",
    description="Real-time AI voice receptionist backend",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "2.0.0"}


@app.websocket("/ws/voice")
async def websocket_voice_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time voice interaction."""
    await websocket.accept()
    
    # Create voice agent
    agent = VoiceAgent(websocket)
    
    # Run conversation loop
    await agent.run()
