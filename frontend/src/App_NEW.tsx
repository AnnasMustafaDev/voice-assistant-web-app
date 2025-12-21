/**
 * Main App Component: Voice AI Agent Interface
 * Central orchestration of all voice interaction features
 * Features: Neural sphere voice bubble, live transcript, expandable chat, glassmorphism UI
 */

import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { VoiceBubble } from './components/VoiceBubble';
import { Transcript } from './components/Transcript';
import { ControlDeck } from './components/ControlDeck';
import { ChatWindow } from './components/ChatWindow';
import { useAgentStore } from './store/agentStore';
import './styles/index.css';

function App() {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isRecording, setIsRecording] = useState(false);

  const {
    agentState,
    setAgentState,
    setCurrentAgent,
    isConnected,
    setIsConnected,
    error,
    setError,
    addTranscriptEntry,
    clearTranscript,
    setAudioAmplitude,
  } = useAgentStore();

  // App configuration from environment
  const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
  const TENANT_ID = import.meta.env.VITE_TENANT_ID || 'demo-tenant';
  const AGENT_ID = import.meta.env.VITE_AGENT_ID || 'receptionist-1';
  const AGENT_NAME = import.meta.env.VITE_AGENT_NAME || 'Reception Agent';

  // Initialize agent
  useEffect(() => {
    setCurrentAgent({
      tenantId: TENANT_ID,
      agentId: AGENT_ID,
      agentName: AGENT_NAME,
    });
  }, [setCurrentAgent]);

  // Simulate WebSocket connection
  useEffect(() => {
    // In production, connect to actual WebSocket
    setIsConnected(true);
    
    return () => {
      setIsConnected(false);
    };
  }, [setIsConnected]);

  // Start listening
  const handleStartListen = useCallback(() => {
    if (!isConnected) {
      setError('Not connected to backend');
      return;
    }

    setAgentState('listening');
    setIsRecording(true);
    setError(null);

    // Simulate microphone input
    const interval = setInterval(() => {
      setAudioAmplitude(Math.random() * 0.8 + 0.2);
    }, 50);

    return () => clearInterval(interval);
  }, [isConnected, setAgentState, setError, setAudioAmplitude]);

  // Stop listening
  const handleStopListen = useCallback(() => {
    setIsRecording(false);
    setAudioAmplitude(0);

    // Transition to thinking
    if (agentState === 'listening') {
      setAgentState('thinking');

      // Simulate thinking time
      setTimeout(() => {
        // Add mock transcript entry
        addTranscriptEntry({
          type: 'user',
          text: 'How can I help you today?',
          timestamp: Date.now(),
        });

        // Transition to speaking
        setAgentState('speaking');

        // Add agent response
        setTimeout(() => {
          addTranscriptEntry({
            type: 'agent',
            text: 'Welcome! How may I assist you?',
            timestamp: Date.now(),
          });

          // Back to idle
          setTimeout(() => {
            setAgentState('idle');
            setAudioAmplitude(0);
          }, 2000);
        }, 500);
      }, 1000);
    }
  }, [agentState, setAgentState, addTranscriptEntry, setAudioAmplitude]);

  const handleClear = useCallback(() => {
    clearTranscript();
    setAgentState('idle');
    setError(null);
  }, [clearTranscript, setAgentState, setError]);

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
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">
            Voice AI Agent
          </h1>
          <p className="text-neon-300 text-sm md:text-base font-medium">
            {agentState.toUpperCase()}
          </p>
        </motion.header>

        {/* Main content area - Neural sphere and controls */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="flex-1 flex flex-col items-center justify-center w-full max-w-2xl"
        >
          {/* Voice Bubble */}
          <VoiceBubble
            onClick={isRecording ? handleStopListen : handleStartListen}
            onStateChange={(state) => {
              // State change handler
            }}
          />

          {/* Error display */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6 px-4 py-3 rounded-lg bg-red-500 bg-opacity-20 border border-red-400 border-opacity-50 text-red-200 text-sm text-center max-w-xs"
            >
              {error}
            </motion.div>
          )}

          {/* Transcript */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="mt-12 md:mt-16 w-full max-w-xl px-6 py-4 rounded-2xl
              bg-white bg-opacity-5 backdrop-blur-xl border border-white border-opacity-10
              shadow-xl"
          >
            <Transcript />
          </motion.div>

          {/* Control Deck */}
          <ControlDeck
            onStartListen={handleStartListen}
            onStopListen={handleStopListen}
            onClear={handleClear}
            isListening={isRecording}
          />
        </motion.div>

        {/* Floating action buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="flex gap-4 items-center"
        >
          {/* Chat button */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setIsChatOpen(!isChatOpen)}
            className={`
              px-6 py-3 rounded-full
              backdrop-blur-lg
              border border-white border-opacity-20
              shadow-lg
              hover:shadow-xl
              transition-all duration-200
              font-medium text-sm
              text-white
              focus:outline-none focus:ring-2 focus:ring-offset-2
              focus:ring-offset-void-900 focus:ring-neon-300
              ${
                isChatOpen
                  ? 'bg-neon-300 bg-opacity-30'
                  : 'bg-white bg-opacity-10 hover:bg-opacity-20'
              }
            `}
          >
            {isChatOpen ? '✕ Close' : '💬 History'}
          </motion.button>

          {/* Status indicator */}
          <div className={`px-3 py-2 rounded-full text-xs font-semibold
            ${
              isConnected
                ? 'bg-neon-300 bg-opacity-20 text-neon-200'
                : 'bg-red-500 bg-opacity-20 text-red-200'
            }
            backdrop-blur-lg border border-white border-opacity-10
          `}>
            {isConnected ? '● Live' : '● Offline'}
          </div>
        </motion.div>
      </div>

      {/* Chat Window */}
      <ChatWindow isOpen={isChatOpen} onToggle={setIsChatOpen} />

      {/* Keyboard shortcuts hint */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 1 }}
        className="fixed bottom-4 left-4 text-white text-opacity-40 text-xs"
      >
        <p>Space or Click bubble to record</p>
      </motion.div>
    </div>
  );
}

export default App;
