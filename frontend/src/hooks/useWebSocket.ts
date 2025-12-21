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
}

export function useWebSocket({ url, onConnect, onDisconnect }: UseWebSocketOptions) {
  const wsRef = useRef<WebSocket | null>(null);
  const { setIsConnected, setError } = useAgentStore();
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    try {
      wsRef.current = new WebSocket(url);

      wsRef.current.onopen = () => {
        console.log('[WebSocket] Connected');
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;
        onConnect?.();
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
        setError('WebSocket connection error');
      };

      wsRef.current.onclose = () => {
        console.log('[WebSocket] Disconnected');
        setIsConnected(false);
        onDisconnect?.();

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
  }, [url, setIsConnected, setError, onConnect, onDisconnect]);

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
    return () => disconnect();
  }, [connect, disconnect]);

  return { send, disconnect, isConnected: wsRef.current?.readyState === WebSocket.OPEN };
}
