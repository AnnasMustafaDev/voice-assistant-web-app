import { create } from 'zustand';
import type { AgentState, TranscriptItem } from '../types';

interface AgentStore {
  // State
  agentState: AgentState;
  transcript: TranscriptItem[];
  isConnected: boolean;
  error: string | null;
  audioAmplitude: number;
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
  audioAmplitude: 0,
  microphoneAmplitude: 0,
  isMicrophoneActive: false,
  currentAgent: null,

  // Action implementations
  setAgentState: (state) => set({ agentState: state }),
  addTranscriptItem: (item) =>
    set((state) => {
      // If item is not final (partial), check if we should update the last item or add new
      if (!item.isFinal) {
        const lastItem = state.transcript[state.transcript.length - 1];
        if (lastItem && !lastItem.isFinal && lastItem.role === item.role) {
          // Update existing partial item
          const newTranscript = [...state.transcript];
          newTranscript[newTranscript.length - 1] = item;
          return { transcript: newTranscript };
        }
      }
      // Otherwise add as new item
      return {
        transcript: [...state.transcript, item],
      };
    }),
  clearTranscript: () => set({ transcript: [] }),
  setIsConnected: (connected) => set({ isConnected: connected }),
  setError: (error) => set({ error }),
  setMicrophoneAmplitude: (amplitude) => set({ audioAmplitude: amplitude, microphoneAmplitude: amplitude }),
  setIsMicrophoneActive: (active) => set({ isMicrophoneActive: active }),
  setCurrentAgent: (agent) => set({ currentAgent: agent }),
}));
