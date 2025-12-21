/**
 * Transcript: Display conversation history with role-based styling
 */

import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAgentStore } from '../store/agentStore';
import { containerVariants, itemVariants } from '../utils/animations';

export const Transcript: React.FC = () => {
  const transcript = useAgentStore((state) => state.transcript);
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
        className="text-center text-slate-400 py-8"
      >
        <p className="text-sm">Start speaking to see transcript</p>
      </motion.div>
    );
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="initial"
      animate="animate"
      className="space-y-3 max-h-64 overflow-y-auto pr-2"
    >
      <AnimatePresence mode="popLayout">
        {transcript.map((item) => (
          <TranscriptItem key={item.id} item={item} />
        ))}
      </AnimatePresence>
      <div ref={endOfTranscriptRef} />
    </motion.div>
  );
};

/**
 * Individual transcript item with role-based styling
 */
interface TranscriptItemProps {
  item: ReturnType<typeof useAgentStore>['transcript'][number];
}

const TranscriptItem: React.FC<TranscriptItemProps> = ({ item }) => {
  const isUser = item.role === 'user';

  return (
    <motion.div
      variants={itemVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      layout
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`
          max-w-xs px-4 py-3 rounded-lg text-sm leading-relaxed
          ${
            isUser
              ? 'bg-purple-100 text-purple-900 rounded-br-none'
              : 'bg-slate-100 text-slate-900 rounded-bl-none'
          }
          ${!item.isFinal ? 'italic opacity-75' : 'font-normal'}
        `}
      >
        <p>{item.text}</p>
        <p className={`text-xs mt-1 ${isUser ? 'text-purple-700' : 'text-slate-600'}`}>
          {isUser ? 'You' : 'Agent'}
          {!item.isFinal && ' (typing...)'}
        </p>
      </div>
    </motion.div>
  );
};
