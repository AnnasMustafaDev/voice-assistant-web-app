/**
 * Hook for microphone input and amplitude analysis
 */

import { useEffect, useRef, useCallback, useState } from 'react';
import { useAgentStore } from '../store/agentStore';

export function useMicrophone() {
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);

  const { setMicrophoneAmplitude, setIsMicrophoneActive } = useAgentStore();

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

      // Create audio context and analyser
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      audioContextRef.current = audioContext;

      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 2048;
      analyserRef.current = analyser;

      source.connect(analyser);

      setIsInitialized(true);
      setIsMicrophoneActive(true);

      // Start analyzing amplitude
      analyzeAmplitude();
    } catch (error) {
      console.error('Failed to access microphone:', error);
      useAgentStore.getState().setError('Microphone access denied');
    }
  }, [setMicrophoneAmplitude, setIsMicrophoneActive]);

  const stopMicrophone = useCallback(() => {
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }

    setIsInitialized(false);
    setIsMicrophoneActive(false);
    setMicrophoneAmplitude(0);
  }, [setMicrophoneAmplitude, setIsMicrophoneActive]);

  const analyzeAmplitude = useCallback(() => {
    if (!analyserRef.current) return;

    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    analyserRef.current.getByteFrequencyData(dataArray);

    let sum = 0;
    for (let i = 0; i < dataArray.length; i++) {
      sum += dataArray[i] * dataArray[i];
    }

    const rms = Math.sqrt(sum / dataArray.length) / 255;
    const amplitude = Math.min(1, rms * 5); // Normalize to 0-1

    setMicrophoneAmplitude(amplitude);

    animationFrameRef.current = requestAnimationFrame(analyzeAmplitude);
  }, [setMicrophoneAmplitude]);

  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  return {
    startMicrophone,
    stopMicrophone,
    isInitialized,
  };
}
