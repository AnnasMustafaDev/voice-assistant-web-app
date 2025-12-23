/**
 * ControlDeck: Glassmorphism control buttons for voice interaction
 * Start/Stop recording and Clear transcript actions
 */

import React from 'react';
import { motion } from 'framer-motion';
import { useAgentStore } from '../store/agentStore';


interface ControlDeckProps {
  onStartListen: () => void;
  onStopListen: () => void;
  onClear: () => void;
  isListening: boolean;
}

export const ControlDeck: React.FC<ControlDeckProps> = ({
  onStartListen,
  onStopListen,
  onClear,

}) => {
  const agentState = useAgentStore((state) => state.agentState);
  const isConnected = useAgentStore((state) => state.isConnected);

  const isActive = agentState === 'listening' || agentState === 'thinking' || agentState === 'speaking';

  const glassButtonClass = `
    relative px-8 py-4 rounded-2xl
    bg-void-900 bg-opacity-60
    backdrop-blur-xl
    border border-white border-opacity-10
    shadow-xl
    hover:bg-opacity-80 hover:border-opacity-20
    hover:shadow-2xl hover:scale-105
    transition-all duration-300
    disabled:opacity-50 disabled:cursor-not-allowed
    font-semibold text-sm tracking-wide
    text-white
    focus:outline-none focus:ring-2 focus:ring-offset-2
    focus:ring-offset-void-900
  `;

  return (
    <div className="fixed bottom-8 left-0 right-0 flex gap-6 justify-center items-center z-50 pointer-events-none">
      <div className="pointer-events-auto flex gap-4 p-2 rounded-3xl bg-black bg-opacity-20 backdrop-blur-md border border-white border-opacity-5">
      {/* Start/Stop Button */}
      <motion.button
        whileTap={{ scale: 0.95 }}
        onClick={isActive ? onStopListen : onStartListen}
        disabled={!isConnected || agentState === 'error'}
        className={`
          ${glassButtonClass}
          ${
            isActive
              ? 'bg-red-500/20 border-red-500/30 text-red-100 hover:bg-red-500/30'
              : 'bg-neon-500/20 border-neon-500/30 text-neon-100 hover:bg-neon-500/30'
          }
          min-w-[140px]
        `}
      >
        <div className="flex items-center justify-center gap-3">
          {isActive ? (
            <>
              <div className="w-2.5 h-2.5 bg-red-400 rounded-full animate-pulse shadow-[0_0_10px_rgba(248,113,113,0.5)]" />
              <span>End Session</span>
            </>
          ) : (
            <>
              <div className="w-2.5 h-2.5 bg-neon-400 rounded-full shadow-[0_0_10px_rgba(45,212,191,0.5)]" />
              <span>Start Chat</span>
            </>
          )}
        </div>
      </motion.button>

      {/* Clear Button */}
      <motion.button
        whileTap={{ scale: 0.95 }}
        onClick={onClear}
        disabled={!isConnected}
        className={`${glassButtonClass} hover:bg-white/10`}
      >
        Clear
      </motion.button>
      </div>

      {/* Connection Status Indicator */}
      <motion.div
        animate={{
          scale: isConnected ? [1, 1.1, 1] : 1,
        }}
        transition={{ duration: 2, repeat: Infinity }}
        className={`
          px-4 py-3 rounded-full
          backdrop-blur-lg
          border border-white border-opacity-20
          flex items-center gap-2
          text-sm font-medium
          ${
            isConnected
              ? 'bg-neon-300 bg-opacity-20 text-neon-200'
              : 'bg-red-500 bg-opacity-20 text-red-200'
          }
        `}
      >
        <div
          className={`
            w-2 h-2 rounded-full
            ${isConnected ? 'bg-neon-300 animate-pulse' : 'bg-red-400 animate-pulse'}
          `}
        />
        {isConnected ? 'Connected' : 'Connecting...'}
      </motion.div>
    </div>
  );
};
