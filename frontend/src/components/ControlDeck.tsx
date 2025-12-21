/**
 * ControlDeck: Glassmorphism control buttons for voice interaction
 * Start/Stop recording and Clear transcript actions
 */

import React from 'react';
import { motion } from 'framer-motion';
import { useAgentStore } from '../store/agentStore';
import type { AgentState } from '../types';

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
  isListening,
}) => {
  const agentState = useAgentStore((state) => state.agentState);
  const isConnected = useAgentStore((state) => state.isConnected);

  const isActive = agentState === 'listening' || agentState === 'thinking' || agentState === 'speaking';

  const buttonVariants = {
    hover: { scale: 1.05, y: -2 },
    tap: { scale: 0.95 },
  };

  const glassButtonClass = `
    relative px-6 py-3 rounded-full
    bg-white bg-opacity-10
    backdrop-blur-lg
    border border-white border-opacity-20
    shadow-lg
    hover:bg-opacity-20 hover:border-opacity-30
    hover:shadow-xl
    transition-all duration-200
    disabled:opacity-50 disabled:cursor-not-allowed
    font-medium text-sm
    text-white
    focus:outline-none focus:ring-2 focus:ring-offset-2
    focus:ring-offset-void-900
  `;

  return (
    <div className="flex gap-4 justify-center items-center mt-8">
      {/* Start/Stop Button */}
      <motion.button
        variants={buttonVariants}
        whileHover="hover"
        whileTap="tap"
        onClick={isActive ? onStopListen : onStartListen}
        disabled={!isConnected || agentState === 'error'}
        className={`
          ${glassButtonClass}
          ${
            isActive
              ? 'focus:ring-red-400 text-red-200'
              : 'focus:ring-neon-300 text-neon-100'
          }
        `}
      >
        <div className="flex items-center gap-2">
          {isActive ? (
            <>
              <div className="w-2 h-2 bg-red-400 rounded-full animate-pulse" />
              Stop
            </>
          ) : (
            <>
              <div className="w-2 h-2 bg-neon-300 rounded-full" />
              Start
            </>
          )}
        </div>
      </motion.button>

      {/* Clear Button */}
      <motion.button
        variants={buttonVariants}
        whileHover="hover"
        whileTap="tap"
        onClick={onClear}
        disabled={!isConnected}
        className={`${glassButtonClass} focus:ring-electric-300 text-electric-200`}
      >
        Clear
      </motion.button>

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
