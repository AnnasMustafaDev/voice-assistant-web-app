/**
 * WebSocket message handlers and utilities
 * Protocol: Only send complete utterances, not streaming chunks
 */

import type { WebSocketMessage, TranscriptItem } from '../types';
import { useAgentStore } from '../store/agentStore';
import { playAudio } from './audio';

const MAX_UTTERANCES_PER_MIN = 10;
let utteranceTimestamps: number[] = [];

function checkRateLimit(): boolean {
  const now = Date.now();
  const oneMinuteAgo = now - 60000;

  // Remove old timestamps
  utteranceTimestamps = utteranceTimestamps.filter((ts) => ts > oneMinuteAgo);

  if (utteranceTimestamps.length >= MAX_UTTERANCES_PER_MIN) {
    console.warn('[WS] Rate limit: Too many utterances in the last minute');
    return false;
  }

  utteranceTimestamps.push(now);
  return true;
}

export function handleWebSocketMessage(message: WebSocketMessage): void {
  const { addTranscriptItem, setError, setAgentState } = useAgentStore.getState();

  switch (message.event) {
    case 'ready':
      console.log('[WS] Server ready');
      break;

    case 'transcript_partial':
      // Handle partial transcript update
      if (message.text) {
        const item: TranscriptItem = {
          id: `transcript-${Date.now()}`,
          role: 'user',
          text: message.text,
          timestamp: Date.now(),
          isFinal: false,
        };
        addTranscriptItem(item);
      }
      break;

    case 'transcript_final':
      // Handle final transcript
      if (message.text) {
        const item: TranscriptItem = {
          id: `transcript-${Date.now()}`,
          role: 'user',
          text: message.text,
          timestamp: Date.now(),
          isFinal: true,
        };
        addTranscriptItem(item);
      }
      break;

    case 'audio_response':
      // Handle agent audio response
      setAgentState('speaking');
      if (message.data) {
        playAudio(message.data)
          .then(() => {
            setAgentState('idle');
          })
          .catch((err) => {
            console.error('[WS] Audio playback error:', err);
            setAgentState('idle');
          });
      } else if (message.text) {
        // Agent sent a text response
        const item: TranscriptItem = {
          id: `agent-${Date.now()}`,
          role: 'agent',
          text: message.text,
          timestamp: Date.now(),
          isFinal: true,
        };
        addTranscriptItem(item);
        setAgentState('idle');
      }
      break;

    case 'error':
      const errorMsg = message.message || message.error || 'Unknown error occurred';
      console.error('[WS] Server error:', errorMsg);
      setError(errorMsg);
      setAgentState('error');

      // Handle rate limiting specifically
      if (message.code === 429 || errorMsg.includes('rate')) {
        console.warn('[WS] Rate limited - waiting before retrying');
      }
      break;

    default:
      console.warn('[WS] Unknown message type:', message.event);
  }
}

/**
 * Send audio utterance (not streaming chunks!)
 */
export function sendAudioUtterance(
  ws: WebSocket,
  base64WavData: string,
  durationMs: number
): boolean {
  if (ws.readyState !== WebSocket.OPEN) {
    console.error('[WS] WebSocket not connected');
    return false;
  }

  if (!checkRateLimit()) {
    useAgentStore.getState().setError('Rate limited: Max 10 utterances per minute');
    return false;
  }

  const message = {
    type: 'audio_utterance',
    audio: base64WavData,
    duration_ms: durationMs,
  };

  console.log('[WS] Sending utterance', { durationMs });
  ws.send(JSON.stringify(message));
  useAgentStore.getState().setAgentState('thinking');
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
    type: 'init',
    tenant_id: tenantId,
    agent_id: agentId,
    language: language,
    conversation_id: `conv-${Date.now()}`,
  };

  console.log('[WS] Sending init');
  ws.send(JSON.stringify(message));
}

/**
 * Send control message
 */
export function sendControl(ws: WebSocket, action: 'start_listening' | 'stop_listening'): void {
  if (ws.readyState !== WebSocket.OPEN) {
    return;
  }

  const message = { type: action };
  ws.send(JSON.stringify(message));
}
