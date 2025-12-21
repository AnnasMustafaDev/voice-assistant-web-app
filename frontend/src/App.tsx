import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { VoiceBubble } from './components/VoiceBubble';
import { Transcript } from './components/Transcript';
import { StatusIndicator } from './components/StatusIndicator';
import { useWebSocket } from './hooks/useWebSocket';
import { useMicrophone } from './hooks/useMicrophone';
import { useAgentStore } from './store/agentStore';
import { encodeAudioToWAV } from './utils/audio';
import { createAudioChunkMessage } from './utils/websocket';
import './styles/globals.css';

interface AppConfig {
  backendUrl: string;
  tenantId: string;
  agentId: string;
  agentName: string;
}

const APP_CONFIG: AppConfig = {
  backendUrl: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000',
  tenantId: import.meta.env.VITE_TENANT_ID || 'demo-tenant',
  agentId: import.meta.env.VITE_AGENT_ID || 'receptionist-1',
  agentName: import.meta.env.VITE_AGENT_NAME || 'Reception Agent',
};

function App() {
  const [isListening, setIsListening] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);

  const {
    agentState,
    setAgentState,
    setCurrentAgent,
    error,
    setError,
  } = useAgentStore();

  const { startMicrophone, stopMicrophone, isInitialized } = useMicrophone();

  const wsUrl = `${APP_CONFIG.backendUrl.replace(/^http/, 'ws')}/voice/stream?tenant_id=${APP_CONFIG.tenantId}&agent_id=${APP_CONFIG.agentId}`;

  const { send } = useWebSocket({
    url: wsUrl,
    onConnect: () => {
      setCurrentAgent({
        tenantId: APP_CONFIG.tenantId,
        agentId: APP_CONFIG.agentId,
        agentName: APP_CONFIG.agentName,
      });
    },
  });

  // Initialize microphone and agent info
  useEffect(() => {
    startMicrophone();
    setCurrentAgent({
      tenantId: APP_CONFIG.tenantId,
      agentId: APP_CONFIG.agentId,
      agentName: APP_CONFIG.agentName,
    });

    return () => {
      stopMicrophone();
    };
  }, []);

  // Handle voice bubble click
  const handleVoiceBubbleClick = async () => {
    if (!isInitialized) {
      setError('Microphone not initialized');
      return;
    }

    if (isListening) {
      // Stop listening
      stopListening();
    } else {
      // Start listening
      startListening();
    }
  };

  const startListening = async () => {
    try {
      setIsListening(true);
      setAgentState('listening');
      setError(null);

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: false,
        },
      });

      const recorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm',
      });

      const chunks: Blob[] = [];

      recorder.ondataavailable = (event) => {
        chunks.push(event.data);
      };

      recorder.onstop = async () => {
        setIsListening(false);
        stream.getTracks().forEach((track) => track.stop());

        const audioBlob = new Blob(chunks, { type: 'audio/webm' });
        await sendAudioToServer(audioBlob);
      };

      recorder.start();
      setMediaRecorder(recorder);
    } catch (error) {
      console.error('Error starting microphone:', error);
      setError('Failed to access microphone');
      setAgentState('error');
      setIsListening(false);
    }
  };

  const stopListening = () => {
    if (mediaRecorder) {
      mediaRecorder.stop();
      setMediaRecorder(null);
      setIsListening(false);
      setAgentState('thinking');
    }
  };

  const sendAudioToServer = async (audioBlob: Blob) => {
    try {
      const arrayBuffer = await audioBlob.arrayBuffer();
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

      // Convert to WAV and encode to base64
      const wavBlob = await encodeAudioToWAV(audioBuffer);
      const reader = new FileReader();

      reader.onload = () => {
        const base64Data = (reader.result as string).split(',')[1];
        const message = createAudioChunkMessage(base64Data);
        send(message);
      };

      reader.readAsDataURL(wavBlob);
    } catch (error) {
      console.error('Error processing audio:', error);
      setError('Failed to process audio');
      setAgentState('error');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex flex-col">
      {/* Header */}
      <StatusIndicator />

      {/* Main Content */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md"
        >
          {/* Title */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-center mb-12"
          >
            <h1 className="text-3xl font-bold text-slate-900 mb-2">
              {APP_CONFIG.agentName}
            </h1>
            <p className="text-slate-600">Voice-powered conversation</p>
          </motion.div>

          {/* Voice Bubble */}
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="flex justify-center mb-12"
          >
            <VoiceBubble onClick={handleVoiceBubbleClick} />
          </motion.div>

          {/* Instruction Text */}
          {agentState === 'idle' && !error && (
            <motion.p
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.3 }}
              className="text-center text-sm text-slate-600 mb-8"
            >
              Click the bubble above and start speaking. It will listen, process your message, and respond.
            </motion.p>
          )}

          {/* Transcript Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="bg-white rounded-lg shadow-sm border border-slate-200 p-6"
          >
            <h2 className="text-lg font-semibold text-slate-900 mb-4">Conversation</h2>
            <Transcript />
          </motion.div>
        </motion.div>
      </div>

      {/* Footer */}
      <motion.footer
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="border-t border-slate-200 bg-white py-4 px-6"
      >
        <p className="text-center text-xs text-slate-500">
          Powered by AI Voice Agent • {isInitialized ? '✓ Microphone Ready' : '✗ Microphone Not Ready'}
        </p>
      </motion.footer>
    </div>
  );
}

export default App;
