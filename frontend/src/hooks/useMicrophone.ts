/**
 * Hook for microphone input and amplitude analysis
 */

import { useEffect, useRef, useCallback, useState } from 'react';
import { useAgentStore } from '../store/agentStore';
import { encodeWAV } from '../utils/audio';

import { stopAudio } from '../utils/audio';

interface UseMicrophoneOptions {
  onAudioData?: (base64Data: string) => void;
}

export function useMicrophone({ onAudioData }: UseMicrophoneOptions = {}) {
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const silenceCounterRef = useRef(0);
  const isSpeakingRef = useRef(false);

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

      // Create script processor for audio capture
      // Buffer size 4096 ~ 0.25s at 16kHz, or ~0.1s at 44.1kHz
      const processor = audioContext.createScriptProcessor(4096, 1, 1);
      processorRef.current = processor;

      processor.onaudioprocess = async (e) => {
        if (!onAudioData) return;

        const inputData = e.inputBuffer.getChannelData(0);
        
        // Simple VAD (Voice Activity Detection)
        let sum = 0;
        for (let i = 0; i < inputData.length; i++) {
          sum += inputData[i] * inputData[i];
        }
        const rms = Math.sqrt(sum / inputData.length);
        
        // Threshold for speech detection (adjust as needed)
        if (rms > 0.02) {
          silenceCounterRef.current = 0;
          if (!isSpeakingRef.current) {
            isSpeakingRef.current = true;
            // User started speaking, stop agent audio
            stopAudio();
          }
        } else {
          silenceCounterRef.current++;
          if (silenceCounterRef.current > 10) { // ~1 second of silence
            isSpeakingRef.current = false;
          }
        }

        // Clone data because encodeWAV might modify or we want to be safe
        const samples = new Float32Array(inputData);
        
        try {
          const blob = encodeWAV(samples, audioContext.sampleRate, 1, 16);
          const reader = new FileReader();
          reader.onloadend = () => {
            if (typeof reader.result === 'string') {
              const base64 = reader.result.split(',')[1];
              onAudioData(base64);
            }
          };
          reader.readAsDataURL(blob);
        } catch (err) {
          console.error('Error encoding audio:', err);
        }
      };

      source.connect(analyser);
      analyser.connect(processor);
      processor.connect(audioContext.destination); // Necessary for script processor to run

      setIsInitialized(true);
      setIsMicrophoneActive(true);

      // Start analyzing amplitude
      analyzeAmplitude();
    } catch (error) {
      console.error('Failed to access microphone:', error);
      useAgentStore.getState().setError('Microphone access denied');
    }
  }, [setMicrophoneAmplitude, setIsMicrophoneActive, onAudioData]);

  const stopMicrophone = useCallback(() => {
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }

    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current = null;
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
