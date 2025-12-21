/**
 * VoiceBubble: Core voice interaction component with state-based animations
 */

import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAgentStore } from '../store/agentStore';
import { voiceBubbleVariants, innerCircleVariants } from '../utils/animations';
import type { AgentState } from '../types';

interface VoiceBubbleProps {
  onStateChange?: (state: AgentState) => void;
  onClick?: () => void;
}

export const VoiceBubble: React.FC<VoiceBubbleProps> = ({ onStateChange, onClick }) => {
  const agentState = useAgentStore((state) => state.agentState);
  const microphoneAmplitude = useAgentStore((state) => state.microphoneAmplitude);
  const error = useAgentStore((state) => state.error);

  useEffect(() => {
    onStateChange?.(agentState);
  }, [agentState, onStateChange]);

  // Calculate dynamic scale based on microphone amplitude during listening
  const amplitudeScale = agentState === 'listening' ? 1 + microphoneAmplitude * 0.15 : 1;

  return (
    <div className="flex flex-col items-center justify-center">
      <motion.button
        variants={voiceBubbleVariants}
        initial="idle"
        animate={agentState === 'error' ? 'error' : agentState}
        onClick={onClick}
        className={`
          relative w-40 h-40 rounded-full flex items-center justify-center
          transition-colors duration-200
          ${
            agentState === 'error'
              ? 'bg-gradient-to-br from-red-500 to-red-600'
              : 'bg-gradient-to-br from-purple-500 to-purple-700'
          }
          hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-purple-400 focus:ring-offset-2
          disabled:opacity-50 disabled:cursor-not-allowed
        `}
        aria-label={`Voice bubble - ${agentState}`}
      >
        {/* Outer glow effect */}
        <div
          className={`
            absolute inset-0 rounded-full blur-2xl opacity-30
            ${agentState === 'error' ? 'bg-red-500' : 'bg-purple-500'}
            transition-all duration-200
          `}
        />

        {/* Inner animated circle */}
        <motion.div
          variants={innerCircleVariants}
          initial="idle"
          animate={agentState === 'error' ? 'error' : agentState}
          style={{ scale: amplitudeScale }}
          className={`
            relative w-20 h-20 rounded-full
            ${
              agentState === 'error'
                ? 'bg-red-300'
                : 'bg-white'
            }
          `}
        >
          {/* Center dot */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div
              className={`
                w-3 h-3 rounded-full
                ${agentState === 'error' ? 'bg-red-600' : 'bg-purple-600'}
              `}
            />
          </div>

          {/* State indicator icon */}
          <StateIcon state={agentState} />
        </motion.div>

        {/* Ripple effect for listening state */}
        {agentState === 'listening' && <ListeningRipple />}
      </motion.button>

      {/* Status text */}
      <motion.p
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        transition={{ duration: 0.3 }}
        className={`
          mt-6 text-sm font-medium uppercase tracking-wider
          ${
            agentState === 'error'
              ? 'text-red-600'
              : 'text-slate-700'
          }
        `}
      >
        {getStatusText(agentState)}
      </motion.p>

      {/* Error message */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-3 text-center text-sm text-red-600 max-w-xs"
        >
          {error}
        </motion.div>
      )}
    </div>
  );
};

/**
 * State-specific icon component
 */
const StateIcon: React.FC<{ state: AgentState }> = ({ state }) => {
  switch (state) {
    case 'listening':
      return (
        <motion.div
          animate={{ scale: [0.8, 1.2, 0.8] }}
          transition={{ duration: 0.8, repeat: Infinity }}
          className="absolute inset-0 flex items-center justify-center"
        >
          <svg
            className="w-8 h-8 text-purple-700"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path d="M12 15c1.66 0 3-1.34 3-3V6c0-1.66-1.34-3-3-3S9 4.34 9 6v6c0 1.66 1.34 3 3 3z" />
          </svg>
        </motion.div>
      );

    case 'thinking':
      return (
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
          className="absolute inset-0 flex items-center justify-center"
        >
          <svg
            className="w-8 h-8 text-purple-700"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </motion.div>
      );

    case 'speaking':
      return (
        <motion.div
          animate={{ scale: [0.9, 1.1, 0.9] }}
          transition={{ duration: 0.6, repeat: Infinity }}
          className="absolute inset-0 flex items-center justify-center"
        >
          <svg
            className="w-8 h-8 text-purple-700"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path d="M12 1C6.48 1 2 5.48 2 11s4.48 10 10 10 10-4.48 10-10S17.52 1 12 1zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 7 15.5 7 14 7.67 14 8.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 7 8.5 7 7 7.67 7 8.5 7.67 10 8.5 10zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z" />
          </svg>
        </motion.div>
      );

    case 'error':
      return (
        <svg
          className="w-8 h-8 text-red-700"
          fill="currentColor"
          viewBox="0 0 24 24"
        >
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
        </svg>
      );

    case 'idle':
    default:
      return (
        <svg
          className="w-8 h-8 text-purple-700"
          fill="currentColor"
          viewBox="0 0 24 24"
        >
          <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z" />
        </svg>
      );
  }
};

/**
 * Listening state ripple effect
 */
const ListeningRipple: React.FC = () => (
  <>
    {[0, 1, 2].map((i) => (
      <motion.div
        key={i}
        animate={{
          scale: [1, 2.5],
          opacity: [0.8, 0],
        }}
        transition={{
          duration: 0.8,
          delay: i * 0.15,
          repeat: Infinity,
        }}
        className="absolute inset-0 rounded-full border-2 border-purple-400"
      />
    ))}
  </>
);

/**
 * Get human-readable status text
 */
function getStatusText(state: AgentState): string {
  const statusMap: Record<AgentState, string> = {
    idle: 'Ready to listen',
    listening: 'Listening...',
    thinking: 'Thinking...',
    speaking: 'Speaking...',
    error: 'Error occurred',
  };
  return statusMap[state];
}
