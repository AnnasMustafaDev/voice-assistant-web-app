/**
 * Transcript: Live transcript display with real-time updates
 * Shows user and agent messages with auto-scroll and word highlighting
 */

import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAgentStore } from '../store/agentStore';

export const Transcript: React.FC = () => {
  const transcript = useAgentStore((state) => state.transcript);
  const agentState = useAgentStore((state) => state.agentState);
  const endOfTranscriptRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest message
  useEffect(() => {
    endOfTranscriptRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, [transcript]);

  if (transcript.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.2 }}
        className="text-center py-12"
      >
        <div className="text-white text-opacity-60">
          <p className="text-sm">Start speaking to see real-time transcript</p>
          <div className="mt-4 flex gap-2 justify-center opacity-50">
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                animate={{ opacity: [0.3, 1] }}
                transition={{ delay: i * 0.2, duration: 0.8, repeat: Infinity }}
                className="w-2 h-2 rounded-full bg-neon-300"
              />
            ))}
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="space-y-2 max-h-64 overflow-y-auto pr-2"
    >
      <AnimatePresence mode="popLayout">
        {transcript.map((entry, idx) => (
          <TranscriptEntry key={idx} entry={entry} agentState={agentState} />
        ))}
      </AnimatePresence>
      <div ref={endOfTranscriptRef} />
    </motion.div>
  );
};

/**
 * TranscriptEntry: Individual transcript entry with role-based styling
 */
interface TranscriptEntryProps {
  entry: any;
  agentState: string;
}

const TranscriptEntry: React.FC<TranscriptEntryProps> = ({ entry }) => {
  const isUser = entry.type === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, x: isUser ? 10 : -10 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: isUser ? 10 : -10 }}
      layout
      transition={{ duration: 0.2 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`
          max-w-xs px-4 py-2 rounded-xl text-sm leading-relaxed
          backdrop-blur-sm border border-opacity-20 border-white
          ${
            isUser
              ? 'bg-neon-300 bg-opacity-15 text-neon-100 rounded-br-none'
              : 'bg-electric-300 bg-opacity-15 text-electric-100 rounded-bl-none'
          }
        `}
      >
        <p>{entry.text}</p>
        <p className={`text-xs mt-1 ${isUser ? 'text-neon-300 opacity-70' : 'text-electric-300 opacity-70'}`}>
          {isUser ? 'You' : 'Agent'}
        </p>
      </div>
    </motion.div>
  );
};
