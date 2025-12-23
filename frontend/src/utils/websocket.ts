/**
 * WebSocket message handlers and utilities
 */

import type { WebSocketMessage, TranscriptItem } from '../types';
import { useAgentStore } from '../store/agentStore';
import { playAudio } from './audio';

export function handleWebSocketMessage(message: WebSocketMessage): void {
  const { addTranscriptItem, setError, setAgentState } = useAgentStore.getState();

  switch (message.event) {
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
          .then(() => setAgentState('idle'))
          .catch((err) => {
            console.error('Audio playback error:', err);
            setAgentState('error');
          });
      }
      break;

    case 'status':
      // Handle status updates
      if (message.status === 'thinking') {
        setAgentState('thinking');
      }
      break;

    case 'error':
      setError(message.error || 'Unknown error occurred');
      setAgentState('error');
      break;
  }
}

export function createAudioChunkMessage(base64Data: string): WebSocketMessage {
  return {
    event: 'audio_chunk',
    data: base64Data,
  };
}
