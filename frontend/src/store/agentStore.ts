import { create } from 'zustand';
import type { AgentState, TranscriptItem } from '../types';

interface AgentStore {
  // State
  agentState: AgentState;
  transcript: TranscriptItem[];
  isConnected: boolean;
  error: string | null;
  microphoneAmplitude: number;
  isMicrophoneActive: boolean;
  currentAgent: {
    tenantId: string;
    agentId: string;
    agentName: string;
  } | null;

  // Actions
  setAgentState: (state: AgentState) => void;
  addTranscriptItem: (item: TranscriptItem) => void;
  clearTranscript: () => void;
  setIsConnected: (connected: boolean) => void;
  setError: (error: string | null) => void;
  setMicrophoneAmplitude: (amplitude: number) => void;
  setIsMicrophoneActive: (active: boolean) => void;
  setCurrentAgent: (agent: { tenantId: string; agentId: string; agentName: string } | null) => void;
}

export const useAgentStore = create<AgentStore>((set) => ({
  // Initial state
  agentState: 'idle',
  transcript: [],
  isConnected: false,
  error: null,
  microphoneAmplitude: 0,
  isMicrophoneActive: false,
  currentAgent: null,

  // Action implementations
  setAgentState: (state) => set({ agentState: state }),
  addTranscriptItem: (item) =>
    set((state) => ({
      transcript: [...state.transcript, item],
    })),
  clearTranscript: () => set({ transcript: [] }),
  setIsConnected: (connected) => set({ isConnected: connected }),
  setError: (error) => set({ error }),
  setMicrophoneAmplitude: (amplitude) => set({ microphoneAmplitude: amplitude }),
  setIsMicrophoneActive: (active) => set({ isMicrophoneActive: active }),
  setCurrentAgent: (agent) => set({ currentAgent: agent }),
}));
