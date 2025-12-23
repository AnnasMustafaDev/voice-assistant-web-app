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

  // Filter transcript to only show user and agent messages (no status)
  const messages = transcript.filter(item => item.role === 'user' || item.role === 'agent');

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Overlay backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={() => onToggle(false)}
            className="fixed inset-0 bg-black bg-opacity-30 backdrop-blur-sm z-40"
          />

          {/* Right-side panel */}
          <motion.div
            initial={{ opacity: 0, x: 400 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 400 }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
            className="fixed right-0 top-0 bottom-0 w-full max-w-md
              bg-gradient-to-br from-white via-white to-blue-50
              backdrop-blur-xl
              border-l border-black border-opacity-10
              shadow-2xl
              flex flex-col
              z-50"
          >
            {/* Header */}
            <div className="px-6 py-4 border-b border-black border-opacity-10
              bg-gradient-to-r from-blue-50 to-purple-50"
            >
              <div className="flex justify-between items-center">
                <h2 className="text-black font-bold text-lg">Conversation</h2>
                <motion.button
                  whileHover={{ scale: 1.1, rotate: 90 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => onToggle(false)}
                  className="w-8 h-8 rounded-full flex items-center justify-center
                    hover:bg-black hover:bg-opacity-10
                    transition-colors duration-200
                    text-black text-xl font-light"
                >
                  ✕
                </motion.button>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-6 py-4 space-y-3">
              {messages.length === 0 ? (
                <div className="flex items-center justify-center h-full text-center">
                  <p className="text-black text-opacity-40 text-sm">
                    No messages yet. Start speaking!
                  </p>
                </div>
              ) : (
                messages.map((entry, idx) => (
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
                        max-w-xs px-4 py-3 rounded-2xl
                        ${
                          entry.role === 'user'
                            ? 'bg-gradient-to-br from-blue-400 to-blue-500 text-white rounded-br-none shadow-md'
                            : 'bg-gray-200 text-black rounded-bl-none shadow-sm'
                        }
                        text-sm break-words
                      `}
                    >
                      <p className="text-xs font-semibold opacity-70 mb-1">
                        {entry.role === 'user' ? '👤 You' : '🤖 Agent'}
                      </p>
                      <p className="leading-relaxed">{entry.text}</p>
                    </div>
                  </motion.div>
                ))
              )}
              <div ref={endRef} />
            </div>

            {/* Footer */}
            <div className="px-6 py-3 border-t border-black border-opacity-10
              bg-gray-50 text-xs text-black text-opacity-50 text-center"
            >
              {messages.length} messages
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
