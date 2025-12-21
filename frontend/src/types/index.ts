export type AgentState = 'idle' | 'listening' | 'thinking' | 'speaking' | 'error';

export interface TranscriptItem {
  id: string;
  role: 'user' | 'agent';
  text: string;
  timestamp: number;
  isFinal: boolean;
}

export interface WebSocketMessage {
  event: 'audio_chunk' | 'transcript_partial' | 'transcript_final' | 'audio_response' | 'error' | 'status';
  data?: string; // base64 encoded audio or transcript text
  text?: string;
  status?: string;
  error?: string;
}

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
