/**
 * Hook for WebSocket connection management
 * Protocol: Send complete utterances (not streaming chunks)
 */

import { useEffect, useRef, useCallback } from 'react';
import { useAgentStore } from '../store/agentStore';
import { handleWebSocketMessage, sendInit, sendAudioUtterance } from '../utils/websocket';
import type { WebSocketMessage } from '../types';

interface UseWebSocketOptions {
  url: string;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onUtterance?: (base64WavData: string, durationMs: number) => void;
  config?: {
    tenantId: string;
    agentId: string;
    language?: string;
  };
}

export function useWebSocket({
  url,
  onConnect,
  onDisconnect,
  onUtterance,
  config,
}: UseWebSocketOptions) {
  const wsRef = useRef<WebSocket | null>(null);
  const { setIsConnected, setError, setAgentState } = useAgentStore();
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  // Store callbacks in refs to prevent unnecessary reconnections
  const onConnectRef = useRef(onConnect);
  const onDisconnectRef = useRef(onDisconnect);
  const onUtteranceRef = useRef(onUtterance);
  const configRef = useRef(config);

  useEffect(() => {
    onConnectRef.current = onConnect;
    onDisconnectRef.current = onDisconnect;
    onUtteranceRef.current = onUtterance;
    configRef.current = config;
  }, [onConnect, onDisconnect, onUtterance, config]);

  const connect = useCallback(() => {
    try {
      // Close existing connection if any
      if (wsRef.current) {
        if (wsRef.current.readyState === WebSocket.OPEN) return;
        wsRef.current.close();
      }

      console.log('[WS] Connecting to', url);
      wsRef.current = new WebSocket(url);

      wsRef.current.onopen = () => {
        console.log('[WS] Connected');
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;

        // Send initial configuration
        if (configRef.current && wsRef.current) {
          sendInit(
            wsRef.current,
            configRef.current.tenantId,
            configRef.current.agentId,
            configRef.current.language || 'en'
          );
        }

        onConnectRef.current?.();
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          handleWebSocketMessage(message);
        } catch (error) {
          console.error('[WS] Failed to parse message:', error);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('[WS] Error:', error);
        setError('WebSocket connection error');
      };

      wsRef.current.onclose = () => {
        console.log('[WS] Disconnected');
        setIsConnected(false);
        setAgentState('idle');
        onDisconnectRef.current?.();

        // Attempt reconnection
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
          console.log(`[WS] Reconnecting in ${delay}ms...`);
          setTimeout(connect, delay);
        } else {
          setError('Failed to connect to server after multiple attempts. Please refresh.');
        }
      };
    } catch (error) {
      console.error('[WS] Connection failed:', error);
      setError('Failed to establish WebSocket connection');
    }
  }, [url, setIsConnected, setError, setAgentState]);

  const sendUtterance = useCallback(
    (base64WavData: string, durationMs: number) => {
      if (wsRef.current) {
        return sendAudioUtterance(wsRef.current, base64WavData, durationMs);
      }
      return false;
    },
    []
  );

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
    sendUtterance,
    isConnected: useAgentStore((state) => state.isConnected),
  };
}
