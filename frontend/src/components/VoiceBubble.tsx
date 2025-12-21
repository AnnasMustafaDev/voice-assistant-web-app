/**
 * NeuralSphere: Advanced voice bubble with glassmorphism and 5-state animations
 * States: idle (breathing), listening (amplitude-based), thinking (shimmer), 
 * speaking (pulsing), error (shake)
 */

import React, { useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import { useAgentStore } from '../store/agentStore';
import type { AgentState } from '../types';

interface VoiceBubbleProps {
  onStateChange?: (state: AgentState) => void;
  onClick?: () => void;
}

// State-specific color mappings
const STATE_COLORS = {
  idle: { bg: 'from-void-500 to-void-700', glow: 'rgba(46, 16, 101, 0.5)' },
  listening: { bg: 'from-neon-300 to-neon-400', glow: 'rgba(6, 182, 212, 0.6)' },
  thinking: { bg: 'from-neural-400 to-neural-500', glow: 'rgba(217, 70, 239, 0.5)' },
  speaking: { bg: 'from-electric-300 to-electric-400', glow: 'rgba(217, 70, 239, 0.8)' },
  error: { bg: 'from-red-500 to-red-600', glow: 'rgba(239, 68, 68, 0.7)' },
};

export const VoiceBubble: React.FC<VoiceBubbleProps> = ({ onStateChange, onClick }) => {
  const agentState = useAgentStore((state) => state.agentState);
  const audioAmplitude = useAgentStore((state) => state.audioAmplitude);

  useEffect(() => {
    onStateChange?.(agentState);
  }, [agentState, onStateChange]);

  // Calculate dynamic scale based on audio amplitude
  const amplitudeScale = useMemo(() => {
    if (agentState === 'listening') return 1 + audioAmplitude * 0.25;
    if (agentState === 'speaking') return 1 + audioAmplitude * 0.3;
    return 1;
  }, [audioAmplitude, agentState]);

  // Animation variants for each state
  const bubbleVariants = {
    idle: {
      scale: [1, 1.05, 1],
      transition: { duration: 3, repeat: Infinity, repeatType: 'reverse' as const },
    },
    listening: {
      scale: amplitudeScale,
      transition: { duration: 0.1 },
    },
    thinking: {
      opacity: [0.8, 1, 0.8],
      transition: { duration: 1.5, repeat: Infinity, repeatType: 'reverse' as const },
    },
    speaking: {
      scale: amplitudeScale,
      transition: { duration: 0.08 },
    },
    error: {
      x: [0, -8, 8, -8, 8, 0],
      transition: { duration: 0.5 },
    },
  };

  const innerCircleVariants = {
    idle: { scale: 0.4, opacity: 0.6 },
    listening: {
      scale: [0.5, 0.8, 0.6],
      opacity: [0.7, 1, 0.7],
      transition: { duration: 0.4, repeat: Infinity, repeatType: 'reverse' as const },
    },
    thinking: {
      scale: 0.7,
      rotate: 360,
      opacity: 0.9,
      transition: { rotate: { duration: 2, repeat: Infinity, repeatType: 'loop' as const } },
    },
    speaking: {
      scale: [0.4, 0.85, 0.5, 0.8, 0.45],
      opacity: [0.7, 1, 0.7, 1, 0.7],
      transition: { duration: 0.6, repeat: Infinity, repeatType: 'reverse' as const },
    },
    error: { scale: 0.4, opacity: 1 },
  };

  const glowVariants = {
    idle: {
      boxShadow: `0 0 40px ${STATE_COLORS.idle.glow}, 0 0 80px ${STATE_COLORS.idle.glow}`,
      transition: { duration: 2, repeat: Infinity, repeatType: 'reverse' as const },
    },
    listening: {
      boxShadow: [
        `0 0 40px ${STATE_COLORS.listening.glow}`,
        `0 0 80px ${STATE_COLORS.listening.glow}`,
        `0 0 40px ${STATE_COLORS.listening.glow}`,
      ],
      transition: { duration: 1.5, repeat: Infinity, repeatType: 'reverse' as const },
    },
    thinking: {
      boxShadow: [
        `0 0 50px ${STATE_COLORS.thinking.glow}`,
        `0 0 100px ${STATE_COLORS.thinking.glow}`,
        `0 0 50px ${STATE_COLORS.thinking.glow}`,
      ],
      transition: { duration: 1, repeat: Infinity, repeatType: 'reverse' as const },
    },
    speaking: {
      boxShadow: [
        `0 0 60px ${STATE_COLORS.speaking.glow}`,
        `0 0 120px ${STATE_COLORS.speaking.glow}`,
        `0 0 60px ${STATE_COLORS.speaking.glow}`,
      ],
      transition: { duration: 0.8, repeat: Infinity, repeatType: 'reverse' as const },
    },
    error: {
      boxShadow: [
        `0 0 40px ${STATE_COLORS.error.glow}`,
        `0 0 80px ${STATE_COLORS.error.glow}`,
        `0 0 40px ${STATE_COLORS.error.glow}`,
      ],
      transition: { duration: 0.6, repeat: Infinity, repeatType: 'reverse' as const },
    },
  };

  const colors = STATE_COLORS[agentState];

  return (
    <div className="flex flex-col items-center justify-center">
      {/* Outer glow layer */}
      <motion.div
        variants={glowVariants}
        initial="idle"
        animate={agentState}
        className="absolute w-48 h-48 rounded-full"
        aria-hidden="true"
      />

      {/* Main bubble container with glassmorphism */}
      <motion.button
        variants={bubbleVariants}
        initial="idle"
        animate={agentState}
        onClick={onClick}
        className={`
          relative w-40 h-40 rounded-full flex items-center justify-center
          bg-gradient-to-br ${colors.bg}
          backdrop-blur-xl
          border border-white border-opacity-20
          shadow-2xl
          hover:shadow-2xl hover:border-opacity-30
          focus:outline-none focus:ring-2 focus:ring-offset-2
          focus:ring-offset-void-900 focus:ring-neon-300
          transition-all duration-200
          disabled:opacity-50 disabled:cursor-not-allowed
          cursor-pointer
          group
        `}
        aria-label={`Neural voice sphere - ${agentState}`}
        type="button"
      >
        {/* Inner animated circle - represents neural activity */}
        <motion.div
          variants={innerCircleVariants}
          initial="idle"
          animate={agentState}
          className={`
            absolute inset-0 m-auto
            rounded-full
            ${agentState === 'thinking' ? 'border-2 border-dashed border-white border-opacity-50' : 'bg-white bg-opacity-20'}
            pointer-events-none
          `}
          style={{
            width: '60%',
            height: '60%',
          }}
        />

        {/* Shimmer effect for thinking state */}
        {agentState === 'thinking' && (
          <div
            className="absolute inset-0 rounded-full overflow-hidden pointer-events-none"
            style={{
              background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)',
              backgroundSize: '200% 200%',
              animation: 'shimmer 2s infinite',
            }}
          />
        )}

        {/* Status indicator dot */}
        <div
          className={`
            absolute top-2 right-2 w-3 h-3 rounded-full
            ${
              agentState === 'idle'
                ? 'bg-neon-300 animate-pulse'
                : agentState === 'listening'
                  ? 'bg-neon-300 animate-bounce'
                  : agentState === 'thinking'
                    ? 'bg-neural-300 animate-spin'
                    : agentState === 'speaking'
                      ? 'bg-electric-300 animate-pulse'
                      : 'bg-red-400 animate-pulse'
            }
            shadow-lg
          `}
        />

        {/* Center label - shows state in lowercase */}
        <span className="text-xs font-semibold text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none">
          {agentState.toUpperCase().slice(0, 3)}
        </span>
      </motion.button>

      {/* Particle effects around bubble */}
      {(agentState === 'listening' || agentState === 'speaking') && (
        <ParticleField state={agentState} />
      )}

      <style>{`
        @keyframes shimmer {
          0% {
            background-position: -200% center;
          }
          100% {
            background-position: 200% center;
          }
        }
      `}</style>
    </div>
  );
};

// Particle field component for dynamic visualization
const ParticleField: React.FC<{ state: AgentState }> = ({ state }) => {
  const isListening = state === 'listening';
  
  return (
    <div className="absolute w-56 h-56 rounded-full pointer-events-none">
      {Array.from({ length: 8 }).map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-1 h-1 rounded-full bg-white"
          animate={{
            x: [0, Math.cos((i / 8) * Math.PI * 2) * 50],
            y: [0, Math.sin((i / 8) * Math.PI * 2) * 50],
            opacity: [0.5, 0, 0.5],
          }}
          transition={{
            duration: isListening ? 1.5 : 0.8,
            repeat: Infinity,
            delay: i * 0.1,
          }}
        />
      ))}
    </div>
  );
};
