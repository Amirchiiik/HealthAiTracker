import { useRef, useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  sendMessage: (message: any) => void;
  lastMessage: WebSocketMessage | null;
  demoMode: boolean;
  setDemoMode: (mode: boolean) => void;
  connectionAttempts: number;
}

export const useWebSocket = (): UseWebSocketReturn => {
  const { user } = useAuth();
  const ws = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionAttempts, setConnectionAttempts] = useState(0);
  const [demoMode, setDemoMode] = useState(true); // Enable demo mode by default
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);

  const connect = () => {
    // Skip WebSocket connection in demo mode
    if (demoMode) {
      console.log('🎭 Demo Mode: WebSocket connection skipped');
      setIsConnected(true);
      return;
    }

    const token = localStorage.getItem('access_token');
    if (!token || connectionAttempts >= 3) {
      console.log('⚠️ WebSocket: Max connection attempts reached or no token available');
      return;
    }

    try {
      const wsUrl = `ws://localhost:8000/ws/${token}`;
      console.log('🔌 Attempting WebSocket connection...');
      
      ws.current = new WebSocket(wsUrl);
      
      ws.current.onopen = () => {
        console.log('🟢 WebSocket connected');
        setIsConnected(true);
        setConnectionAttempts(0);
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('📨 WebSocket message received:', data);
          setLastMessage(data);
        } catch (error) {
          console.error('❌ Error parsing WebSocket message:', error);
        }
      };

      ws.current.onclose = () => {
        console.log('🔴 WebSocket disconnected');
        setIsConnected(false);
        
        // Only attempt reconnection if not in demo mode and under attempt limit
        if (!demoMode && connectionAttempts < 3) {
          setConnectionAttempts(prev => prev + 1);
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log(`🔄 Reconnecting WebSocket (attempt ${connectionAttempts + 1}/3)...`);
            connect();
          }, 3000 * (connectionAttempts + 1)); // Exponential backoff
        }
      };

      ws.current.onerror = (error) => {
        console.log('⚠️ WebSocket error (switching to demo mode):', error);
        setIsConnected(false);
        // Automatically switch to demo mode on persistent errors
        if (connectionAttempts >= 2) {
          setDemoMode(true);
          setIsConnected(true);
          console.log('🎭 Switched to demo mode due to connection issues');
        }
      };
    } catch (error) {
      console.error('❌ WebSocket connection error:', error);
      // Fallback to demo mode
      setDemoMode(true);
      setIsConnected(true);
    }
  };

  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
    setIsConnected(false);
  };

  const sendMessage = (message: any) => {
    if (demoMode) {
      console.log('🎭 Demo Mode: Message would be sent:', message);
      return Promise.resolve();
    }

    if (ws.current && isConnected) {
      try {
        ws.current.send(JSON.stringify(message));
        return Promise.resolve();
      } catch (error) {
        console.error('❌ Error sending WebSocket message:', error);
        return Promise.reject(error);
      }
    } else {
      console.warn('⚠️ WebSocket not connected, cannot send message');
      return Promise.reject(new Error('WebSocket not connected'));
    }
  };

  useEffect(() => {
    if (user) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [user]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, []);

  return {
    isConnected,
    sendMessage,
    lastMessage,
    demoMode,
    setDemoMode,
    connectionAttempts
  };
}; 