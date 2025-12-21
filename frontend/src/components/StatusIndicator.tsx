/**
 * StatusIndicator: Display connection and system status
 */

import React from 'react';
import { motion } from 'framer-motion';
import { useAgentStore } from '../store/agentStore';

export const StatusIndicator: React.FC = () => {
  const isConnected = useAgentStore((state) => state.isConnected);
  const currentAgent = useAgentStore((state) => state.currentAgent);
  const agentState = useAgentStore((state) => state.agentState);

  return (
    <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-white">
      {/* Connection Status */}
      <div className="flex items-center gap-3">
        <motion.div
          animate={{
            scale: isConnected ? 1 : [1, 1.1, 1],
            opacity: isConnected ? 1 : [1, 0.6, 1],
          }}
          transition={{
            scale: { duration: 0.2 },
            opacity: { duration: 0.8, repeat: isConnected ? 0 : Infinity },
          }}
          className={`
            w-3 h-3 rounded-full
            ${isConnected ? 'bg-green-500' : 'bg-amber-500'}
          `}
        />
        <span className="text-sm font-medium text-slate-700">
          {isConnected ? 'Connected' : 'Connecting...'}
        </span>
      </div>

      {/* Agent Info */}
      {currentAgent && (
        <div className="text-center">
          <p className="text-sm font-semibold text-slate-900">{currentAgent.agentName}</p>
          <p className="text-xs text-slate-500">{agentState}</p>
        </div>
      )}

      {/* Session Info */}
      <div className="text-right">
        <p className="text-xs text-slate-500">
          {new Date().toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </p>
      </div>
    </div>
  );
};
