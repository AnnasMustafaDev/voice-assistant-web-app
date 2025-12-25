/**
 * Main App Component: Voice AI Agent Interface
 * STRICT MICROPHONE LIFECYCLE CONTROL
 * 1. Mic only active during "Listening" state
 * 2. Mic disabled during TTS playback (agent speaking)
 * 3. Push-to-talk triggers listening
 * 4. Release button finalizes utterance
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { motion } from 'framer-motion';
import { VoiceBubble } from './components/VoiceBubble';
import { Transcript } from './components/Transcript';
import { ControlDeck } from './components/ControlDeck';
import { ChatWindow } from './components/ChatWindow';
import { useAgentStore } from './store/agentStore';
import { useWebSocket } from './hooks/useWebSocket';
import { useMicrophone } from './hooks/useMicrophone';
import './index.css';

function App() {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const micActiveRef = useRef(false);
  const audioContextRef = useRef<AudioContext | null>(null);

  const {
    agentState,
    setAgentState,
    setCurrentAgent,
    setError,
    clearTranscript,
    isListening,
    setIsListening,
  } = useAgentStore();

  // App configuration from environment
  const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
  const TENANT_ID = import.meta.env.VITE_TENANT_ID || 'demo-tenant';
  const AGENT_ID = import.meta.env.VITE_AGENT_ID || 'receptionist-1';
  const AGENT_NAME = import.meta.env.VITE_AGENT_NAME || 'Reception Agent';

  // Initialize agent once
  useEffect(() => {
    setCurrentAgent({
      tenantId: TENANT_ID,
      agentId: AGENT_ID,
      agentName: AGENT_NAME,
    });
  }, []);

  // WebSocket - created once, never reconnects automatically
  const wsConfigRef = useRef({
    tenantId: TENANT_ID,
    agentId: AGENT_ID,
  });

  const { sendUtterance, isConnected: wsConnected } = useWebSocket({
    url: `${BACKEND_URL.replace('http', 'ws')}/voice/stream`,
    config: wsConfigRef.current,
    onConnect: useCallback(() => {
      console.log('[App] WebSocket connected');
    }, []),
    onDisconnect: useCallback(() => {
      console.log('[App] WebSocket disconnected');
      // STOP MIC IMMEDIATELY if disconnected
      if (micActiveRef.current) {
        console.warn('[App] WebSocket lost - killing microphone');
        stopMicrophoneImmediate();
      }
    }, [])
  });

  // Handle complete utterance from VAD
  const handleUtterance = useCallback((base64WavData: string, durationMs: number) => {
    console.log(`[App] Utterance finalized: ${durationMs}ms`);
    
    if (!wsConnected) {
      console.error('[App] Cannot send - WebSocket not connected');
      setError('Connection lost');
      return;
    }

    // STOP MIC IMMEDIATELY after utterance is finalized
    micActiveRef.current = false;
    
    try {
      sendUtterance(base64WavData, durationMs);
      setIsListening(false);
      if (agentState === 'listening') {
        setAgentState('thinking');
      }
    } catch (err) {
      console.error('[App] Failed to send utterance:', err);
      setError('Failed to send audio');
    }
  }, [wsConnected, sendUtterance, setIsListening, agentState, setAgentState, setError]);

  // Microphone hook - ONLY operates during listening state
  const { startMicrophone, stopMicrophone, forceFinalize } = useMicrophone({
    onUtterance: handleUtterance
  });

  // Stop microphone immediately (hard stop)
  const stopMicrophoneImmediate = useCallback(async () => {
    console.log('[App] Hard stopping microphone');
    try {
      stopMicrophone();
      // Kill all audio tracks forcefully
      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        await audioContextRef.current.close();
        audioContextRef.current = null;
      }
    } catch (err) {
      console.error('[App] Error stopping mic:', err);
    }
  }, [stopMicrophone]);

  // Start listening (ONLY on explicit user action)
  const handleStartListen = useCallback(async () => {
    if (!wsConnected) {
      setError('Not connected - please refresh');
      return;
    }

    if (agentState === 'speaking') {
      console.warn('[App] Cannot record while speaking');
      setError('Wait for agent to finish speaking');
      return;
    }

    try {
      console.log('[App] Starting microphone - user pressing button');
      micActiveRef.current = true;
      setIsListening(true);
      setAgentState('listening');
      setError(null);
      await startMicrophone();
    } catch (err) {
      console.error('[App] Microphone failed:', err);
      micActiveRef.current = false;
      setIsListening(false);
      setError('Microphone error - check permissions');
    }
  }, [wsConnected, agentState, startMicrophone, setIsListening, setAgentState, setError]);

  // Stop listening (release button)
  const handleStopListen = useCallback(() => {
    console.log('[App] User released button - finalizing utterance');
    forceFinalize();
    // Don't call stopMicrophone() yet - let VAD finalize first
  }, [forceFinalize]);

  const handleInterrupt = useCallback(async () => {
    console.log('[App] INTERRUPT - Stopping everything');
    // Hard stop microphone immediately
    micActiveRef.current = false;
    setIsListening(false);
    
    try {
      // Stop recording if active
      stopMicrophone();
      // Hard kill audio context
      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        await audioContextRef.current.close();
        audioContextRef.current = null;
      }
    } catch (err) {
      console.error('[App] Error during interrupt:', err);
    }
    
    // Reset to idle
    setAgentState('idle');
    setError(null);
  }, [stopMicrophone, setIsListening, setAgentState, setError]);

  const handleClear = useCallback(() => {
    console.log('[App] Clearing');
    clearTranscript();
    setAgentState('idle');
    setError(null);
    setIsListening(false);
    micActiveRef.current = false;
  }, [clearTranscript, setAgentState, setError, setIsListening]);

  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-void-900 via-void-800 to-void-900">
        {/* Animated gradient blur background */}
        <motion.div
          animate={{
            background: [
              'radial-gradient(circle at 20% 50%, rgba(46, 16, 101, 0.3), transparent 50%)',
              'radial-gradient(circle at 80% 50%, rgba(6, 182, 212, 0.2), transparent 50%)',
              'radial-gradient(circle at 50% 80%, rgba(217, 70, 239, 0.2), transparent 50%)',
            ],
          }}
          transition={{ duration: 8, repeat: Infinity }}
          className="absolute inset-0"
        />
        
        {/* Noise texture overlay */}
        <div className="absolute inset-0 opacity-5 mix-blend-overlay" />
      </div>

      {/* Main content */}
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-between p-6 md:p-8">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="w-full text-center mb-8 md:mb-12"
        >
          <div className="flex items-center justify-center gap-3 mb-3">
            <div className="h-1 w-8 bg-gradient-to-r from-cyan-400 to-purple-500 rounded-full" />
            <h1 className="text-4xl md:text-5xl font-black text-white tracking-tight">
              AI Agent
            </h1>
            <div className="h-1 w-8 bg-gradient-to-r from-purple-500 to-cyan-400 rounded-full" />
          </div>
          <p className="text-cyan-300 text-xs md:text-sm font-semibold tracking-widest uppercase letter-spacing">
            STATUS: <span className="text-neon-300 font-bold">{agentState}</span>
          </p>
        </motion.header>

        {/* Main content area - Neural sphere and controls */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="flex-1 flex flex-col items-center justify-start w-full max-w-2xl gap-26 "
        >
          {/* Voice Bubble - moved up */}
          <motion.div
            initial={{ y: 20 }}
            animate={{ y: 0 }}
            transition={{ duration: 0.4 }}
          >
            <VoiceBubble
              isActive={isListening}
            />
          </motion.div>

          {/* Transcript - below voice bubble, above buttons */}
          <div className="w-full px-4 z-40">
            <Transcript />
          </div>

          {/* Control Deck - Push-to-talk controls */}
          <ControlDeck
            onStartListen={handleStartListen}
            onStopListen={handleStopListen}
            onForceFinalize={forceFinalize}
            onInterrupt={handleInterrupt}
            onClear={handleClear}
          />
        </motion.div>

      </div>

      {/* Chat Window - Right side panel */}
      <ChatWindow isOpen={isChatOpen} onToggle={setIsChatOpen} />

      {/* Keyboard shortcuts hint */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 1 }}
        className="fixed bottom-4 left-4 text-white text-opacity-40 text-xs"
      >
        <p>Hold button to record • Release to finalize</p>
      </motion.div>
    </div>
  );
}

export default App;
