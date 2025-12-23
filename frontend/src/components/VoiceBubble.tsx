import React from 'react';
import { motion } from 'framer-motion';
import type { Easing } from 'framer-motion';
import { useAgentStore } from '../store/agentStore';

interface VoiceBubbleProps {
  isActive?: boolean;
  onClick?: () => void;
}

export const VoiceBubble: React.FC<VoiceBubbleProps> = ({ isActive = false, onClick }) => {
  const agentState = useAgentStore((state) => state.agentState);

  // Animation variants for different states
  const getBubbleVariant = () => {
    const easeInOut: Easing = "easeInOut";
    const linear: Easing = "linear";

    switch (agentState) {
      case 'listening':
        return {
          scale: [1, 1.05, 1],
          borderRadius: [
            "50% 50% 50% 50% / 50% 50% 50% 50%",
            "55% 45% 50% 50% / 50% 55% 45% 50%",
            "50% 50% 50% 50% / 50% 50% 50% 50%"
          ],
          transition: {
            duration: 4,
            repeat: Infinity,
            ease: easeInOut
          }
        };
      case 'thinking':
        return {
          scale: [1, 0.95, 1.05, 1],
          borderRadius: [
            "60% 40% 30% 70% / 60% 30% 70% 40%",
            "30% 60% 70% 40% / 50% 60% 30% 60%",
            "60% 40% 30% 70% / 60% 30% 70% 40%"
          ],
          rotate: [0, 180, 360],
          transition: {
            duration: 2,
            repeat: Infinity,
            ease: linear
          }
        };
      case 'speaking':
        return {
          scale: [1, 1.1, 0.95, 1.15, 1],
          borderRadius: [
            "50% 50% 50% 50% / 50% 50% 50% 50%",
            "60% 40% 40% 60% / 50% 40% 60% 50%",
            "40% 60% 60% 40% / 60% 50% 40% 60%",
            "50% 50% 50% 50% / 50% 50% 50% 50%"
          ],
          transition: {
            duration: 1.5,
            repeat: Infinity,
            ease: easeInOut
          }
        };
      default: // idle
        return {
          scale: 1,
          borderRadius: "50%",
          transition: { duration: 0.5 }
        };
    }
  };

  const getColor = () => {
    switch (agentState) {
      case 'listening': return 'bg-neon-400';
      case 'thinking': return 'bg-electric-400';
      case 'speaking': return 'bg-neon-300';
      default: return 'bg-white';
    }
  };

  return (
    <div 
      className={`relative flex justify-center items-center h-64 w-64 cursor-pointer
        ${isActive ? 'opacity-100' : 'opacity-80'}
        transition-opacity duration-200
      `}
      onClick={onClick}
    >
      {/* Outer Glow / Aura */}
      <motion.div
        animate={{
          scale: agentState === 'speaking' ? [1, 1.2, 1] : [1, 1.1, 1],
          opacity: [0.3, 0.1, 0.3],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className={`absolute inset-0 rounded-full blur-3xl ${getColor()} opacity-20`}
      />

      {/* Inner Jellyfish Blob */}
      <motion.div
        animate={getBubbleVariant()}
        className={`
          relative w-48 h-48
          backdrop-blur-md
          bg-gradient-to-br from-white/10 to-white/5
          border border-white/20
          shadow-[0_0_50px_rgba(0,0,0,0.2)]
          flex items-center justify-center
          overflow-hidden
          cursor-pointer
        `}
        style={{
          boxShadow: `inset 0 0 20px rgba(255,255,255,0.1), 0 0 30px ${agentState === 'listening' ? 'rgba(52, 211, 153, 0.2)' : 'rgba(167, 139, 250, 0.2)'}`
        }}
      >
        {/* Core */}
        <motion.div
          animate={{
            scale: [1, 0.8, 1],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className={`w-24 h-24 rounded-full ${getColor()} opacity-80 blur-xl`}
        />
        
        {/* Surface reflections */}
        <div className="absolute top-4 left-8 w-12 h-6 bg-white opacity-20 rounded-full blur-sm transform -rotate-12" />
        <div className="absolute bottom-6 right-8 w-8 h-4 bg-white opacity-10 rounded-full blur-sm transform -rotate-12" />
      </motion.div>
    </div>
  );
};
