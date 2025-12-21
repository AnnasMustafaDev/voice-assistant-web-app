/**
 * Audio utility functions for encoding/decoding and analysis
 */

export async function encodeAudioToWAV(audioBuffer: AudioBuffer): Promise<Blob> {
  const numberOfChannels = audioBuffer.numberOfChannels;
  const sampleRate = audioBuffer.sampleRate;
  const bitDepth = 16;

  const channelData = [];
  for (let i = 0; i < numberOfChannels; i++) {
    channelData.push(audioBuffer.getChannelData(i));
  }

  const bufferLength = audioBuffer.length;
  const audioData = new Float32Array(bufferLength * numberOfChannels);

  let offset = 0;
  const channelLength = audioBuffer.length;
  for (let i = 0; i < channelLength; i++) {
    for (let channel = 0; channel < numberOfChannels; channel++) {
      audioData[offset++] = channelData[channel][i];
    }
  }

  return encodeWAV(audioData, sampleRate, numberOfChannels, bitDepth);
}

function encodeWAV(
  samples: Float32Array,
  sampleRate: number,
  numChannels: number,
  bitDepth: number
): Blob {
  const bytesPerSample = bitDepth / 8;
  const blockAlign = numChannels * bytesPerSample;

  const data = new Uint8Array(44 + samples.length * bytesPerSample);

  // WAV header
  writeString(data, 0, 'RIFF');
  writeInt32LE(data, 4, 36 + samples.length * bytesPerSample);
  writeString(data, 8, 'WAVE');

  // fmt sub-chunk
  writeString(data, 12, 'fmt ');
  writeInt32LE(data, 16, 16); // Subchunk1Size
  writeInt16LE(data, 20, 1); // AudioFormat (PCM)
  writeInt16LE(data, 22, numChannels);
  writeInt32LE(data, 24, sampleRate);
  writeInt32LE(data, 28, sampleRate * blockAlign);
  writeInt16LE(data, 32, blockAlign);
  writeInt16LE(data, 34, bitDepth);

  // data sub-chunk
  writeString(data, 36, 'data');
  writeInt32LE(data, 40, samples.length * bytesPerSample);

  // Write audio samples
  let index = 44;
  const volume = 0.8;
  for (let i = 0; i < samples.length; i++) {
    const sample = Math.max(-1, Math.min(1, samples[i])) * volume;
    writeInt16LE(data, index, sample < 0 ? sample * 0x8000 : sample * 0x7fff);
    index += 2;
  }

  return new Blob([data], { type: 'audio/wav' });
}

function writeString(view: Uint8Array, offset: number, string: string): void {
  for (let i = 0; i < string.length; i++) {
    view[offset + i] = string.charCodeAt(i);
  }
}

function writeInt32LE(view: Uint8Array, offset: number, value: number): void {
  view[offset] = value & 0xff;
  view[offset + 1] = (value >> 8) & 0xff;
  view[offset + 2] = (value >> 16) & 0xff;
  view[offset + 3] = (value >> 24) & 0xff;
}

function writeInt16LE(view: Uint8Array, offset: number, value: number): void {
  view[offset] = value & 0xff;
  view[offset + 1] = (value >> 8) & 0xff;
}

/**
 * Convert base64 string to Blob
 */
export function base64ToBlob(base64: string, mimeType: string = 'audio/wav'): Blob {
  const binaryString = atob(base64);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return new Blob([bytes], { type: mimeType });
}

/**
 * Analyze audio data for amplitude (0-1)
 */
export function analyzeAudioAmplitude(audioBuffer: AudioBuffer): number {
  const channelData = audioBuffer.getChannelData(0);
  let rms = 0;

  for (let i = 0; i < channelData.length; i++) {
    rms += channelData[i] * channelData[i];
  }

  rms = Math.sqrt(rms / channelData.length);
  return Math.min(1, rms * 3); // Normalize and amplify
}

/**
 * Create audio context
 */
export function getOrCreateAudioContext(): AudioContext {
  const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
  return new AudioContextClass();
}
