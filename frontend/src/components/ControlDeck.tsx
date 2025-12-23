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
  onClear: () => void;
}

export const ControlDeck: React.FC<ControlDeckProps> = ({
  onStartListen,
  onStopListen,
  onForceFinalize,
  onClear,
}) => {
  const agentState = useAgentStore((state) => state.agentState);
  const isConnected = useAgentStore((state) => state.isConnected);
  const isListening = useAgentStore((state) => state.isListening);
  const error = useAgentStore((state) => state.error);
  const [isPushDown, setIsPushDown] = useState(false);

  // Button states
  const isThinking = agentState === 'thinking';
  const isSpeaking = agentState === 'speaking';
  const isActive = isListening;

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

  // Visual feedback for error state
  if (error) {
    return (
      <div className="fixed bottom-8 left-0 right-0 flex gap-6 justify-center items-center z-50 pointer-events-none">
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
    <div className="fixed bottom-8 left-0 right-0 flex gap-6 justify-center items-center z-50 pointer-events-none">
      <div className="pointer-events-auto flex flex-col gap-4">
        {/* Push-to-Talk Button */}
        <motion.button
          whileTap={{ scale: 0.95 }}
          onMouseDown={handleMouseDown}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          onTouchStart={handleTouchStart}
          onTouchEnd={handleTouchEnd}
          disabled={!isConnected}
          className={`
            ${glassButtonClass}
            min-w-[200px] py-6
            ${
              isPushDown
                ? 'bg-red-500/20 border-red-500/30 text-red-100 scale-95'
                : isActive
                  ? 'bg-yellow-500/20 border-yellow-500/30 text-yellow-100'
                  : isThinking
                    ? 'bg-blue-500/20 border-blue-500/30 text-blue-100'
                    : isSpeaking
                      ? 'bg-green-500/20 border-green-500/30 text-green-100'
                      : 'bg-neon-500/20 border-neon-500/30 text-neon-100'
            }
          `}
        >
          <div className="flex items-center justify-center gap-3">
            {isPushDown ? (
              <>
                <div className="w-3 h-3 bg-red-400 rounded-full animate-pulse shadow-[0_0_10px_rgba(248,113,113,0.5)]" />
                <span>🎙 Recording...</span>
              </>
            ) : isThinking ? (
              <>
                <div className="w-3 h-3 bg-blue-400 rounded-full animate-pulse" />
                <span>🧠 Thinking...</span>
              </>
            ) : isSpeaking ? (
              <>
                <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse" />
                <span>🔊 Speaking...</span>
              </>
            ) : isActive ? (
              <>
                <div className="w-3 h-3 bg-yellow-400 rounded-full animate-pulse" />
                <span>🎤 Listening...</span>
              </>
            ) : (
              <>
                <div className="w-3 h-3 bg-neon-400 rounded-full shadow-[0_0_10px_rgba(45,212,191,0.5)]" />
                <span>🎙 Hold to talk</span>
              </>
            )}
          </div>
        </motion.button>

        {/* Control Buttons */}
        <div className="flex gap-4 p-2 rounded-3xl bg-black bg-opacity-20 backdrop-blur-md border border-white border-opacity-5 justify-center">
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={onClear}
            disabled={!isConnected}
            className={`${glassButtonClass} hover:bg-white/10`}
          >
            Clear
          </motion.button>
        </div>
      </div>

      {/* Connection Status */}
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
        {isConnected ? 'Ready' : 'Connecting...'}
      </motion.div>
    </div>
  );
};
