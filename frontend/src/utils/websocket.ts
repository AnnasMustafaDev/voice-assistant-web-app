/**
 * WebSocket message handlers and utilities
 * Protocol: Audio streaming with complete utterance detection
 */

import type { TranscriptItem } from '../types';
import { useAgentStore } from '../store/agentStore';
import { playAudio } from './audio';

export function handleWebSocketMessage(message: any): void {
  const { addTranscriptItem, setError, setAgentState } = useAgentStore.getState();
  const now = Date.now();

  switch (message.event) {
    case 'ready':
      console.log('[WS] Server ready', message.conversation_id);
      setAgentState('listening');
      break;

    case 'user_transcript':
      // User's speech was transcribed
      if (message.text) {
        const item: TranscriptItem = {
          id: `user-${message.timestamp || Date.now()}`,
          role: 'user',
          text: message.text,
          timestamp: now,
          isFinal: true,
        };
        addTranscriptItem(item);
      }
      setAgentState('thinking');
      break;

    case 'assistant_transcript':
      // Assistant's response text
      if (message.text) {
        const item: TranscriptItem = {
          id: `assistant-${message.timestamp || Date.now()}`,
          role: 'agent',
          text: message.text,
          timestamp: now,
          isFinal: true,
        };
        addTranscriptItem(item);
      }
      break;

    case 'audio':
      // Audio chunk - play it
      setAgentState('speaking');
      if (message.audio) {
        playAudio(message.audio)
          .catch((err) => {
            if (err.name === 'AbortError') return;
            console.error('[WS] Audio playback error:', err);
          });
      }
      break;

    case 'audio_complete':
      // All audio has been sent
      console.log('[WS] Audio complete');
      setAgentState('listening');
      break;

    case 'error':
      const errorMsg = message.message || 'Unknown error occurred';
      console.error('[WS] Server error:', errorMsg);
      setError(errorMsg);
      setAgentState('error');
      break;

    default:
      console.log('[WS] Message event:', message.event);
  }
}

/**
 * Send audio chunk with latency measurement
 */
export function sendAudioChunk(
  ws: WebSocket,
  base64AudioData: string,
  latencyMs: number = 0
): boolean {
  if (ws.readyState !== WebSocket.OPEN) {
    console.error('[WS] WebSocket not connected');
    return false;
  }

  const message = {
    event: 'audio',
    audio: base64AudioData,
    latency_ms: latencyMs,
  };

  console.log('[WS] Sending audio chunk', { latencyMs });
  ws.send(JSON.stringify(message));
  return true;
}

/**
 * Send initialization message
 */
export function sendInit(
  ws: WebSocket,
  tenantId: string,
  agentId: string,
  language: string = 'en'
): void {
  if (ws.readyState !== WebSocket.OPEN) {
    console.error('[WS] Cannot send init - WebSocket not connected');
    return;
  }

  const message = {
    event: 'init',
    tenant_id: tenantId,
    agent_id: agentId,
    language: language,
  };

  console.log('[WS] Sending init');
  ws.send(JSON.stringify(message));
}

/**
 * Send control message
 */
export function sendControl(ws: WebSocket, action: string): void {
  if (ws.readyState !== WebSocket.OPEN) {
    return;
  }

  const message = { event: action };
  ws.send(JSON.stringify(message));
}

/**
 * Send finalize message - signals backend to process buffered audio immediately
 */
export function sendFinalize(ws: WebSocket): void {
  if (ws.readyState !== WebSocket.OPEN) {
    console.error('[WS] Cannot send finalize - WebSocket not connected');
    return;
  }

  const message = {
    event: 'finalize',
    timestamp: Date.now(),
  };

  console.log('[WS] Sending finalize - button released');
  ws.send(JSON.stringify(message));
}
