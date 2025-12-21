/**
 * ChatWindow: Expandable/collapsible chat history with glassmorphism
 * Shows conversation history with user and agent messages
 */

import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAgentStore } from '../store/agentStore';

interface ChatWindowProps {
  isOpen: boolean;
  onToggle: (open: boolean) => void;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({ isOpen, onToggle }) => {
  const transcript = useAgentStore((state) => state.transcript);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen && endRef.current) {
      endRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [transcript, isOpen]);

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 20, scale: 0.95 }}
          transition={{ duration: 0.3 }}
          className={`
            fixed bottom-24 right-6 w-96 max-h-96 rounded-2xl
            bg-white bg-opacity-10
            backdrop-blur-xl
            border border-white border-opacity-20
            shadow-2xl
            overflow-hidden
            flex flex-col
            z-40
            md:bottom-8 md:right-8
            md:w-full md:max-w-sm
          `}
        >
          {/* Header */}
          <div
            className={`
            px-6 py-4
            border-b border-white border-opacity-10
            flex justify-between items-center
            bg-white bg-opacity-5
          `}
          >
            <h2 className="text-white font-semibold text-lg">Conversation</h2>
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onToggle(false)}
              className={`
                w-8 h-8 rounded-full flex items-center justify-center
                hover:bg-white hover:bg-opacity-20
                transition-colors duration-200
                text-white text-xl
              `}
            >
              ×
            </motion.button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-6 py-4 space-y-3">
            {transcript.length === 0 ? (
              <div className="flex items-center justify-center h-full text-center">
                <p className="text-white text-opacity-50 text-sm">
                  No conversation yet. Start speaking!
                </p>
              </div>
            ) : (
              transcript.map((entry, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: entry.role === 'user' ? 20 : -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.2 }}
                  className={`
                    flex gap-2 mb-3
                    ${entry.role === 'user' ? 'justify-end' : 'justify-start'}
                  `}
                >
                  <div
                    className={`
                      max-w-xs px-4 py-2 rounded-lg
                      ${
                        entry.role === 'user'
                          ? 'bg-neon-300 bg-opacity-20 text-neon-100 border border-neon-300 border-opacity-30'
                          : 'bg-electric-300 bg-opacity-20 text-electric-100 border border-electric-300 border-opacity-30'
                      }
                      text-sm
                      break-words
                    `}
                  >
                    <p className="text-xs font-medium opacity-70 mb-1">
                      {entry.role === 'user' ? 'You' : 'Agent'}
                    </p>
                    <p>{entry.text}</p>
                  </div>
                </motion.div>
              ))
            )}
            <div ref={endRef} />
          </div>

          {/* Footer */}
          <div
            className={`
            px-6 py-3
            border-t border-white border-opacity-10
            bg-white bg-opacity-5
            text-xs text-white text-opacity-50
            text-center
          `}
          >
            {transcript.length} messages
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
