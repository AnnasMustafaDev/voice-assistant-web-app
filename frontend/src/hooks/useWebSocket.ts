/**
 * Hook for WebSocket connection management
 */

import { useEffect, useRef, useCallback } from 'react';
import { useAgentStore } from '../store/agentStore';
import { handleWebSocketMessage } from '../utils/websocket';
import type { WebSocketMessage } from '../types';

interface UseWebSocketOptions {
  url: string;
  onConnect?: () => void;
  onDisconnect?: () => void;
  config?: {
    tenantId: string;
    agentId: string;
    language?: string;
  };
}

export function useWebSocket({ url, onConnect, onDisconnect, config }: UseWebSocketOptions) {
  const wsRef = useRef<WebSocket | null>(null);
  const { setIsConnected, setError } = useAgentStore();
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;
  
  // Store callbacks in refs to prevent unnecessary reconnections
  const onConnectRef = useRef(onConnect);
  const onDisconnectRef = useRef(onDisconnect);
  const configRef = useRef(config);

  useEffect(() => {
    onConnectRef.current = onConnect;
    onDisconnectRef.current = onDisconnect;
    configRef.current = config;
  }, [onConnect, onDisconnect, config]);

  const connect = useCallback(() => {
    try {
      // Close existing connection if any
      if (wsRef.current) {
        if (wsRef.current.readyState === WebSocket.OPEN) return;
        wsRef.current.close();
      }

      wsRef.current = new WebSocket(url);

      wsRef.current.onopen = () => {
        console.log('[WebSocket] Connected');
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;
        
        // Send initial configuration
        if (configRef.current && wsRef.current) {
          wsRef.current.send(JSON.stringify({
            tenant_id: configRef.current.tenantId,
            agent_id: configRef.current.agentId,
            language: configRef.current.language || 'en',
          }));
        }

        onConnectRef.current?.();
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          handleWebSocketMessage(message);
        } catch (error) {
          console.error('[WebSocket] Failed to parse message:', error);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('[WebSocket] Error:', error);
        // Don't set error immediately on connection error to avoid UI flicker during retry
      };

      wsRef.current.onclose = () => {
        console.log('[WebSocket] Disconnected');
        setIsConnected(false);
        onDisconnectRef.current?.();

        // Attempt reconnection
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
          console.log(`[WebSocket] Reconnecting in ${delay}ms...`);
          setTimeout(connect, delay);
        } else {
          setError('Failed to connect to server. Please refresh the page.');
        }
      };
    } catch (error) {
      console.error('[WebSocket] Connection failed:', error);
      setError('Failed to connect to WebSocket');
    }
  }, [url, setIsConnected, setError]);

  const send = useCallback((message: WebSocketMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('[WebSocket] Connection not ready');
    }
  }, []);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [connect]);

  return {
    connect,
    disconnect,
    send,
    isConnected: useAgentStore((state) => state.isConnected),
  };
}
