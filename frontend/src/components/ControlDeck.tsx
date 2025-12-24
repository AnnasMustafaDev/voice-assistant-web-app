/**
 * ControlDeck: Push-to-talk and control interface
 * - Hold button to record
 * - Release to finalize utterance
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useAgentStore } from '../store/agentStore';

interface ControlDeckProps {
  onStartListen: () => void;
  onStopListen: () => void;
  onForceFinalize?: () => void;
  onInterrupt: () => void;
  onClear: () => void;
}

export const ControlDeck: React.FC<ControlDeckProps> = ({
  onStartListen,
  onStopListen,
  onForceFinalize,
  onInterrupt,
  onClear,
}) => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const isConnected = useAgentStore((state) => state.isConnected);
  const error = useAgentStore((state) => state.error);
  const transcript = useAgentStore((state) => state.transcript);
  const [isPushDown, setIsPushDown] = useState(false);

  const glassButtonClass = `
    relative px-6 py-3 rounded-2xl
    bg-void-900 bg-opacity-60
    backdrop-blur-xl
    border border-white border-opacity-10
    shadow-xl
    hover:bg-opacity-80 hover:border-opacity-20
    transition-all duration-200
    disabled:opacity-50 disabled:cursor-not-allowed
    font-semibold text-sm tracking-wide
    text-white
    focus:outline-none focus:ring-2 focus:ring-offset-2
    focus:ring-offset-void-900
  `;

  const handleMouseDown = () => {
    if (!isConnected || error) return;
    setIsPushDown(true);
    onStartListen();
  };

  const handleMouseUp = () => {
    if (!isPushDown) return;
    setIsPushDown(false);
    onForceFinalize?.();
    onStopListen();
  };

  const handleTouchStart = () => handleMouseDown();
  const handleTouchEnd = () => handleMouseUp();

  // Show error in a banner if present
  if (error) {
    return (
      <div className="fixed bottom-8 left-0 right-0 flex flex-col gap-4 items-center z-50 pointer-events-none">
        <motion.div
          animate={{ scale: [1, 1.05, 1] }}
          transition={{ duration: 0.5, repeat: Infinity }}
          className="pointer-events-auto px-6 py-3 rounded-2xl
            bg-red-500/20 backdrop-blur-xl
            border border-red-500/30
            shadow-xl
            text-red-100 text-sm font-semibold
            max-w-md text-center"
        >
          ⛔ {error}
        </motion.div>
      </div>
    );
  }

  return (
    <div className="fixed bottom-8 left-0 right-0 flex flex-col gap-6 items-center z-50 pointer-events-none">
      {/* Control Buttons Row */}
      <div className="pointer-events-auto flex gap-3 p-3 rounded-3xl bg-black bg-opacity-20 backdrop-blur-md border border-white border-opacity-5 relative">
        <motion.button
          whileTap={{ scale: 0.95 }}
          onClick={() => {
            onInterrupt();
          }}
          disabled={!isConnected}
          className={`${glassButtonClass}`}
        >
          ⏹ Stop
        </motion.button>

        {/* Record Button - Between Stop and Clear */}
        <motion.button
          whileTap={{ scale: 0.95 }}
          onMouseDown={handleMouseDown}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          onTouchStart={handleTouchStart}
          onTouchEnd={handleTouchEnd}
          disabled={!isConnected}
          className={`
            pointer-events-auto
            ${glassButtonClass}
            ${isPushDown ? 'bg-red-500/20 border-red-500/30 scale-95' : 'hover:scale-105'}
          `}
        >
          <div className="flex items-center justify-center gap-2">
            <div className={`w-2 h-2 rounded-full transition-all ${isPushDown ? 'bg-red-400 animate-pulse' : 'bg-neon-400'}`} />
            <span>{isPushDown ? '🎙 Recording' : '🎤 Hold'}</span>
          </div>
        </motion.button>

        <motion.button
          whileTap={{ scale: 0.95 }}
          onClick={onClear}
          disabled={!isConnected}
          className={`${glassButtonClass}`}
        >
          Clear
        </motion.button>
      </div>

      {/* Connection Status - Simple indicator */}
      <motion.div
        animate={{
          scale: isConnected ? [1, 1.05, 1] : 1,
        }}
        transition={{ duration: 2, repeat: Infinity }}
        className={`
          pointer-events-auto
          px-4 py-2 rounded-full
          backdrop-blur-lg
          border border-white border-opacity-20
          flex items-center gap-2
          text-xs font-medium
          ${isConnected ? 'bg-neon-300/10 text-neon-200' : 'bg-red-500/10 text-red-200'}
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
