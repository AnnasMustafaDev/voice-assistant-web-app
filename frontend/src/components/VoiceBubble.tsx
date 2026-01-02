import React, { useRef, useEffect } from 'react';
import { useAgentStore } from '../store/agentStore';

interface VoiceBubbleProps {
  isActive?: boolean;
  onClick?: () => void;
}

// --- COMPONENT: Neural Sphere (Canvas 3D Particles) ---

interface NeuralSphereProps {
  state: 'idle' | 'listening' | 'thinking' | 'speaking' | string;
}

const NeuralSphere: React.FC<NeuralSphereProps> = ({ state = 'idle' }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let particles: any[] = [];
    let time = 0;

    const getStateConfig = (s: string) => {
      switch (s) {
        case 'listening':
          return {
            baseColor: { r: 94, g: 234, b: 212 }, // Teal-300
            secondaryColor: { r: 45, g: 212, b: 191 }, // Teal-400
            speed: 0.03,
            amplitude: 15,
            radiusMod: 1.1,
            waveFrequency: 6,
            waveSpeed: 3,
            connectionOpacity: 0.15,
            jitter: false
          };
        case 'thinking':
          return {
            baseColor: { r: 255, g: 255, b: 255 },
            secondaryColor: { r: 99, g: 102, b: 241 }, // Indigo-500
            speed: 0.08,
            amplitude: 4,
            radiusMod: 0.9,
            waveFrequency: 10,
            waveSpeed: 5,
            connectionOpacity: 0.3,
            jitter: false
          };
        case 'speaking':
          return {
            baseColor: { r: 45, g: 212, b: 191 }, // Teal
            secondaryColor: { r: 168, g: 85, b: 247 }, // Purple
            speed: 0.04,
            amplitude: 25,
            radiusMod: 1.15,
            waveFrequency: 4,
            waveSpeed: 8,
            connectionOpacity: 0.2,
            jitter: false
          };
        case 'error':
          return {
            baseColor: { r: 251, g: 113, b: 133 }, // Rose
            secondaryColor: { r: 225, g: 29, b: 72 }, // Red
            speed: 0.01,
            amplitude: 5,
            radiusMod: 1.0,
            jitter: true,
            waveFrequency: 1,
            waveSpeed: 1,
            connectionOpacity: 0.05
          };
        case 'idle':
        default:
          return {
            baseColor: { r: 99, g: 102, b: 241 }, // Indigo
            secondaryColor: { r: 129, g: 140, b: 248 }, // Indigo-light
            speed: 0.008,
            amplitude: 5,
            radiusMod: 1.0,
            waveFrequency: 2,
            waveSpeed: 1,
            connectionOpacity: 0.1,
            jitter: false
          };
      }
    };

    const initParticles = () => {
      particles = [];
      const count = 350;
      for (let i = 0; i < count; i++) {
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.acos((Math.random() * 2) - 1);
        particles.push({
          theta,
          phi,
          baseTheta: theta,
          rad: 130, // Base radius
          size: Math.random() * 2.5 + 1,
        });
      }
    };

    const resize = () => {
      if (canvas.parentElement) {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = canvas.parentElement.clientHeight;
        initParticles();
      }
    };

    window.addEventListener('resize', resize);
    resize();

    const render = () => {
      const { width, height } = canvas;
      const cfg = getStateConfig(state);

      ctx.clearRect(0, 0, width, height);

      const cx = width / 2;
      const cy = height / 2;
      time += cfg.speed;

      let shakeX = 0;
      let shakeY = 0;
      if (cfg.jitter) {
        shakeX = (Math.random() - 0.5) * 8;
        shakeY = (Math.random() - 0.5) * 8;
      }

      particles.forEach(p => {
        p.theta = p.baseTheta + time * 0.5;

        let wave = Math.sin((p.phi * cfg.waveFrequency) - (time * cfg.waveSpeed)) * cfg.amplitude;

        if (state === 'speaking') {
          wave += Math.cos((p.theta * 3) + (time * 4)) * (cfg.amplitude * 0.5);
        }

        const radius = (p.rad * cfg.radiusMod) + wave;

        const x = radius * Math.sin(p.phi) * Math.cos(p.theta);
        const y = radius * Math.sin(p.phi) * Math.sin(p.theta);
        const z = radius * Math.cos(p.phi);

        // Simple perspective projection
        const scale = 400 / (400 + z); 
        const x2d = (x * scale) + cx + shakeX;
        const y2d = (y * scale) + cy + shakeY;

        // Depth-based opacity
        const alpha = Math.max(0.1, (z + 120) / 240);
        const mix = (wave / cfg.amplitude + 1) / 2;

        const r = cfg.baseColor.r * (1 - mix) + cfg.secondaryColor.r * mix;
        const g = cfg.baseColor.g * (1 - mix) + cfg.secondaryColor.g * mix;
        const b = cfg.baseColor.b * (1 - mix) + cfg.secondaryColor.b * mix;

        ctx.beginPath();
        ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${alpha * (cfg.connectionOpacity + 0.5)})`;
        ctx.arc(x2d, y2d, p.size * scale, 0, Math.PI * 2);
        ctx.fill();
        
        // Optional: faint connections for "neural" feel
        if (state !== 'error') {
            ctx.shadowBlur = 15;
            ctx.shadowColor = `rgba(${r}, ${g}, ${b}, 0.5)`;
        } else {
            ctx.shadowBlur = 0;
        }
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(animationFrameId);
    };
  }, [state]);

  return <canvas ref={canvasRef} className="w-full h-full block" />;
};

// --- COMPONENT: VoiceBubble (Wrapper) ---

export const VoiceBubble: React.FC<VoiceBubbleProps> = ({ onClick }) => {
  const agentState = useAgentStore((state) => state.agentState);

  return (
    <div 
      className="relative flex justify-center items-center h-64 w-64 cursor-pointer
        rounded-full overflow-hidden"
      onClick={onClick}
    >
      <NeuralSphere state={agentState} />
    </div>
  );
};
