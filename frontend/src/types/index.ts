export type AgentState = 'idle' | 'listening' | 'thinking' | 'speaking' | 'error';

export interface TranscriptItem {
  id: string;
  role: 'user' | 'agent';
  text: string;
  timestamp: number;
  isFinal: boolean;
}

/**
 * WebSocket messages - Client to Server
 */
export type ClientMessage =
  | { type: 'init'; tenant_id: string; agent_id: string; language: string; conversation_id?: string }
  | { type: 'audio_utterance'; audio: string; duration_ms: number }
  | { type: 'start_listening' }
  | { type: 'stop_listening' };

/**
 * WebSocket messages - Server to Client
 */
export type ServerMessage =
  | { event: 'ready'; conversation_id?: string }
  | { event: 'transcript_partial'; text: string }
  | { event: 'transcript_final'; text: string }
  | { event: 'audio_response'; data?: string; text?: string }
  | { event: 'error'; code?: number; message?: string; error?: string };

export type WebSocketMessage = ClientMessage | ServerMessage;

export interface VoiceConfig {
  tenantId: string;
  agentId: string;
  agentName: string;
  backendUrl: string;
}

export interface MicrophoneAnalyzer {
  getAmplitude(): number;
  isActive(): boolean;
}
