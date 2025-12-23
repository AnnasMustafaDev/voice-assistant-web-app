/**
 * Transcript: Live transcript display with real-time updates
 * Shows user and agent messages with auto-scroll and word highlighting
 */

import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAgentStore } from '../store/agentStore';

export const Transcript: React.FC = () => {
  const transcript = useAgentStore((state) => state.transcript);
  const agentState = useAgentStore((state) => state.agentState);
  const [isExpanded, setIsExpanded] = useState(false);
  const endOfTranscriptRef = useRef<HTMLDivElement>(null);

  // Filter to only show messages (user and agent), not status
  const messages = transcript.filter(item => item.role === 'user' || item.role === 'agent');

  // Auto-scroll to latest message
  useEffect(() => {
    if (isExpanded) {
      endOfTranscriptRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [messages, isExpanded]);

  if (messages.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.2 }}
        className="text-center py-8"
      >
        {/* <div className="text-white text-opacity-40 font-light tracking-wide">
          <p className="text-sm">Start speaking to begin conversation</p>
        </div> */}
      </motion.div>
    );
  }

  const latestMessage = messages[messages.length - 1];

  return (
    <motion.div
      layout
      onClick={() => setIsExpanded(!isExpanded)}
      className={`
        relative w-full max-w-xl mx-auto
        rounded-2xl overflow-hidden
        bg-void-900 bg-opacity-40 backdrop-blur-xl
        border border-white border-opacity-10
        shadow-2xl
        cursor-pointer
        transition-all duration-500 ease-out
        ${isExpanded ? 'h-[60vh] z-50' : 'h-20 hover:bg-opacity-50 hover:border-opacity-20'}
      `}
    >
      {/* Header / Handle */}
      <div className="absolute top-0 left-0 right-0 h-6 flex justify-center items-center opacity-30">
        <div className="w-12 h-1 rounded-full bg-white" />
      </div>

      <div className={`p-6 ${isExpanded ? 'h-full overflow-y-auto' : 'h-full flex items-center'}`}>
        <AnimatePresence mode="wait">
          {!isExpanded ? (
            <motion.div
              key="preview"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="w-full"
            >
              <p className="text-white text-opacity-90 text-center truncate px-4 font-medium text-lg">
                <span className={`mr-2 text-xs uppercase tracking-wider opacity-50 ${latestMessage.role === 'user' ? 'text-neon-400' : 'text-electric-400'}`}>
                  {latestMessage.role === 'user' ? 'You' : 'Agent'}
                </span>
                {latestMessage.text}
              </p>
            </motion.div>
          ) : (
            <motion.div
              key="full"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-4 pt-4"
            >
              {messages.map((entry, idx) => (
                <TranscriptEntry key={idx} entry={entry} agentState={agentState} />
              ))}
              <div ref={endOfTranscriptRef} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
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
