/**
 * Hook for microphone input with real-time audio streaming
 * - Streams audio chunks to backend immediately as they're captured
 * - Backend handles VAD and silence detection
 * - Button release triggers finalize on backend
 */

import { useEffect, useRef, useCallback, useState } from 'react';
import { useAgentStore } from '../store/agentStore';
import { encodeWAV, encodePCM, resampleAudio } from '../utils/audio';
import { stopAudio } from '../utils/audio';

const CHUNK_MS = 20;
const TARGET_SAMPLE_RATE = 16000;

interface UseMicrophoneOptions {
  onAudioChunk?: (base64AudioData: string) => void;
  onUtterance?: (base64WavData: string, durationMs: number) => void;
}

interface AudioBuffer {
  chunks: Float32Array[];
  totalSamples: number;
  startTime: number;
}

export function useMicrophone({ onAudioChunk, onUtterance }: UseMicrophoneOptions = {}) {
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  
  // Track if we're currently recording
  const isRecordingRef = useRef(false);
  const bufferRef = useRef<AudioBuffer>({
    chunks: [],
    totalSamples: 0,
    startTime: 0,
  });

  const { setMicrophoneAmplitude, setIsMicrophoneActive } = useAgentStore();

  const finializeUtterance = useCallback(() => {
    if (!onUtterance || bufferRef.current.chunks.length === 0) {
      return;
    }

    console.log('[Mic] Utterance finalized', {
      chunks: bufferRef.current.chunks.length,
      totalSamples: bufferRef.current.totalSamples,
    });

    try {
      // Combine all chunks
      const combinedSamples = new Float32Array(bufferRef.current.totalSamples);
      let offset = 0;
      for (const chunk of bufferRef.current.chunks) {
        combinedSamples.set(chunk, offset);
        offset += chunk.length;
      }

      // Resample to 16kHz if needed
      const currentSampleRate = audioContextRef.current?.sampleRate || 44100;
      let finalSamples: Float32Array = combinedSamples;
      
      if (currentSampleRate !== TARGET_SAMPLE_RATE) {
        const resampled = resampleAudio(combinedSamples, currentSampleRate, TARGET_SAMPLE_RATE);
        finalSamples = new Float32Array(resampled);
      }

      // Encode to WAV
      const blob = encodeWAV(finalSamples, TARGET_SAMPLE_RATE, 1, 16);
      const reader = new FileReader();
      reader.onloadend = () => {
        if (typeof reader.result === 'string') {
          const base64 = reader.result.split(',')[1];
          const durationMs = Math.round((finalSamples.length / TARGET_SAMPLE_RATE) * 1000);
          onUtterance(base64, durationMs);
        }
      };
      reader.readAsDataURL(blob);
    } catch (err) {
      console.error('[Mic] Error finalizing utterance:', err);
    }

    // Reset buffer
    bufferRef.current = { chunks: [], totalSamples: 0, startTime: 0 };
  }, [onUtterance]);

  const startMicrophone = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: false,
        },
      });

      mediaStreamRef.current = stream;
      setIsMicrophoneActive(true);
      isRecordingRef.current = true;

      // Create audio context
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      audioContextRef.current = audioContext;

      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      analyserRef.current = analyser;

      // Create script processor for streaming audio chunks
      const processor = audioContext.createScriptProcessor(2048, 1, 1);
      processorRef.current = processor;

      processor.onaudioprocess = (e) => {
        if (!isRecordingRef.current) return;

        const inputData = e.inputBuffer.getChannelData(0);

        // Calculate RMS energy for visualization
        let sum = 0;
        for (let i = 0; i < inputData.length; i++) {
          sum += inputData[i] * inputData[i];
        }
        const rms = Math.sqrt(sum / inputData.length);
        setMicrophoneAmplitude(rms);

        // Always buffer chunks while recording
        bufferRef.current.chunks.push(new Float32Array(inputData));
        bufferRef.current.totalSamples += inputData.length;

        // Stream audio chunk to backend in real-time
        if (onAudioChunk) {
          try {
            // Resample to 16kHz if needed
            let chunkSamples = new Float32Array(inputData);
            if (audioContext.sampleRate !== TARGET_SAMPLE_RATE) {
              chunkSamples = resampleAudio(chunkSamples, audioContext.sampleRate, TARGET_SAMPLE_RATE);
            }

            // Encode chunk as PCM (no header)
            const blob = encodePCM(chunkSamples, 16);
            const reader = new FileReader();
            reader.onloadend = () => {
              if (typeof reader.result === 'string') {
                const base64 = reader.result.split(',')[1];
                onAudioChunk(base64);
              }
            };
            reader.readAsDataURL(blob);
          } catch (err) {
            console.error('[Mic] Error encoding chunk:', err);
          }
        }
      };

      source.connect(analyser);
      analyser.connect(processor);
      processor.connect(audioContext.destination);

      setIsInitialized(true);
    } catch (error) {
      console.error('[Mic] Failed to access microphone:', error);
      useAgentStore.getState().setError('Microphone access denied');
    }
  }, [setMicrophoneAmplitude, setIsMicrophoneActive, onAudioChunk]);

  const stopMicrophone = useCallback(() => {
    console.log('[Mic] Stopping microphone');
    isRecordingRef.current = false;

    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }

    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current = null;
    }

    if (analyserRef.current) {
      analyserRef.current.disconnect();
      analyserRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close().catch(err => console.error('[Mic] Error closing audio context:', err));
      audioContextRef.current = null;
    }

    setIsInitialized(false);
    setIsMicrophoneActive(false);
    setMicrophoneAmplitude(0);
  }, [setMicrophoneAmplitude, setIsMicrophoneActive]);

  const forceFinalize = useCallback(() => {
    console.log('[Mic] Force finalizing utterance');
    isRecordingRef.current = false;
    stopMicrophone();
  }, [stopMicrophone]);

  useEffect(() => {
    return () => {
      stopMicrophone();
    };
  }, [stopMicrophone]);

  return {
    startMicrophone,
    stopMicrophone,
    forceFinalize,
    isInitialized,
  };
}
