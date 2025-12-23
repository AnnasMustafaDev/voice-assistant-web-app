import React from 'react';
import { motion } from 'framer-motion';
import { useAgentStore } from '../store/agentStore';

interface VoiceBubbleProps {
  isActive?: boolean;
  onClick?: () => void;
}

export const VoiceBubble: React.FC<VoiceBubbleProps> = ({ isActive = false, onClick }) => {
  const agentState = useAgentStore((state) => state.agentState);

  // Gentle squishy animation - always subtle
  const getBubbleVariant = () => {
    if (agentState === 'speaking') {
      // More pronounced squeeze during speaking
      return {
        scaleY: [1, 0.92, 1.08, 1],
        scaleX: [1, 1.08, 0.92, 1],
        transition: {
          duration: 1.2,
          repeat: Infinity,
          ease: "easeInOut" as const
        }
      };
    }
    
    // Gentle idle pulse for all other states
    return {
      scale: [1, 1.03, 1],
      transition: {
        duration: 3,
        repeat: Infinity,
        ease: "easeInOut" as const
      }
    };
  };

  return (
    <div 
      className={`relative flex justify-center items-center h-64 w-64 cursor-pointer
        ${isActive ? 'opacity-100' : 'opacity-80'}
        transition-opacity duration-200
      `}
      onClick={onClick}
    >
      {/* Outer Glow - subtle pulse */}
      <motion.div
        animate={{
          scale: [1, 1.15, 1],
          opacity: [0.2, 0.1, 0.2],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="absolute inset-0 rounded-full blur-3xl bg-neon-400 opacity-20"
      />

      {/* Main Squishy Bubble - keeps it simple and spherical */}
      <motion.div
        animate={getBubbleVariant()}
        className="relative w-48 h-48
          backdrop-blur-md
          bg-gradient-to-br from-white/10 to-white/5
          border border-white/20
          shadow-[0_0_50px_rgba(0,0,0,0.2)]
          flex items-center justify-center
          overflow-hidden
          cursor-pointer
          rounded-full"
        style={{
          boxShadow: `inset 0 0 20px rgba(255,255,255,0.1), 0 0 30px rgba(52, 211, 153, 0.2)`
        }}
      >
        {/* Core pulsing light */}
        <motion.div
          animate={{
            scale: [1, 0.8, 1],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="w-24 h-24 rounded-full bg-neon-400 opacity-60 blur-xl"
        />
        
        {/* Subtle reflections */}
        <div className="absolute top-8 left-12 w-10 h-5 bg-white opacity-20 rounded-full blur-sm" />
      </motion.div>
    </div>
  );
};
