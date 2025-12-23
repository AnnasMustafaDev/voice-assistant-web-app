/**
 * Hook for microphone input with client-side VAD (Voice Activity Detection)
 * - Buffers audio chunks until silence detected
 * - Sends complete utterances (not streaming chunks)
 * - Prevents STT rate limiting
 */

import { useEffect, useRef, useCallback, useState } from 'react';
import { useAgentStore } from '../store/agentStore';
import { encodeWAV, resampleAudio } from '../utils/audio';
import { stopAudio } from '../utils/audio';

const CHUNK_MS = 20;
const SILENCE_THRESHOLD = 0.01; // RMS threshold for silence
const END_SILENCE_MS = 700; // 700ms of silence to end utterance
const TARGET_SAMPLE_RATE = 16000;

interface UseMicrophoneOptions {
  onUtterance?: (base64WavData: string, durationMs: number) => void;
}

interface AudioBuffer {
  chunks: Float32Array[];
  totalSamples: number;
  startTime: number;
}

export function useMicrophone({ onUtterance }: UseMicrophoneOptions = {}) {
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  
  // VAD state
  const isSpeakingRef = useRef(false);
  const silenceDurationRef = useRef(0);
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
    isSpeakingRef.current = false;
    silenceDurationRef.current = 0;
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

      // Create audio context
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      audioContextRef.current = audioContext;

      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      analyserRef.current = analyser;

      // Create script processor (smaller buffer for lower latency)
      // 2048 samples at 44.1kHz = ~46ms, at 16kHz = ~128ms
      const processor = audioContext.createScriptProcessor(2048, 1, 1);
      processorRef.current = processor;

      processor.onaudioprocess = (e) => {
        const inputData = e.inputBuffer.getChannelData(0);

        // Calculate RMS energy
        let sum = 0;
        for (let i = 0; i < inputData.length; i++) {
          sum += inputData[i] * inputData[i];
        }
        const rms = Math.sqrt(sum / inputData.length);

        // Update amplitude visualization
        setMicrophoneAmplitude(rms);

        // VAD logic
        if (rms > SILENCE_THRESHOLD) {
          // Speech detected
          silenceDurationRef.current = 0;
          if (!isSpeakingRef.current) {
            console.log('[Mic] Speech started');
            isSpeakingRef.current = true;
            stopAudio();
            bufferRef.current.startTime = Date.now();
          }
          // Buffer the audio chunk
          bufferRef.current.chunks.push(new Float32Array(inputData));
          bufferRef.current.totalSamples += inputData.length;
        } else if (isSpeakingRef.current) {
          // Silence detected after speech
          silenceDurationRef.current += CHUNK_MS;
          // Keep buffering for a bit (in case of pauses)
          bufferRef.current.chunks.push(new Float32Array(inputData));
          bufferRef.current.totalSamples += inputData.length;

          if (silenceDurationRef.current >= END_SILENCE_MS) {
            console.log('[Mic] Silence detected - finalizing utterance');
            finializeUtterance();
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
  }, [setMicrophoneAmplitude, setIsMicrophoneActive, finializeUtterance]);

  const stopMicrophone = useCallback(() => {
    // Finalize any pending utterance
    if (isSpeakingRef.current && bufferRef.current.chunks.length > 0) {
      finializeUtterance();
    }

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
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    setIsInitialized(false);
    setIsMicrophoneActive(false);
    setMicrophoneAmplitude(0);
  }, [setMicrophoneAmplitude, setIsMicrophoneActive, finializeUtterance]);

  const forceFinalize = useCallback(() => {
    if (isSpeakingRef.current) {
      console.log('[Mic] Force finalizing utterance');
      finializeUtterance();
    }
  }, [finializeUtterance]);

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
