/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Modern futuristic palette
        neural: {
          50: '#faf5ff',
          100: '#f5ebff',
          200: '#e9d5ff',
          300: '#d946ef',
          400: '#c026d3',
          500: '#a21caf',
          600: '#9333ea',
          700: '#7e22ce',
          800: '#6b21a8',
          900: '#581c87',
        },
        // Deep violet to black gradient base
        void: {
          50: '#f3e8ff',
          100: '#ede9fe',
          200: '#ddd6fe',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#2E1065', // Primary brand violet
          600: '#220b63',
          700: '#1a0847',
          800: '#140635',
          900: '#020617', // Deep black
        },
        // Neon cyan accent
        neon: {
          50: '#cffafe',
          100: '#a5f3fc',
          200: '#67e8f9',
          300: '#06b6d4', // Primary cyan
          400: '#0891b2',
          500: '#0e7490',
          600: '#155e75',
          700: '#164e63',
          800: '#1e293b',
          900: '#0f172a',
        },
        // Electric purple accent
        electric: {
          50: '#faf5ff',
          100: '#f3e8ff',
          200: '#e9d5ff',
          300: '#d946ef', // Primary electric purple
          400: '#c026d3',
          500: '#a21caf',
          600: '#9333ea',
          700: '#7e22ce',
          800: '#6b21a8',
          900: '#581c87',
        },
        primary: {
          50: '#f8f7ff',
          100: '#f0edff',
          200: '#e0dbff',
          300: '#d1c5ff',
          400: '#b8a0ff',
          500: '#9f7aff',
          600: '#8a5cff',
          700: '#7544ff',
          800: '#6838e6',
          900: '#5a2fb3',
        },
        slate: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        },
      },
      animation: {
        'pulse-soft': 'pulse-soft 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite',
        'scale-breathe': 'scale-breathe 2s ease-in-out infinite',
      },
      keyframes: {
        'pulse-soft': {
          '0%, 100%': { opacity: '0.3' },
          '50%': { opacity: '1' },
        },
        'glow': {
          '0%, 100%': { boxShadow: '0 0 20px rgba(159, 122, 255, 0.3)' },
          '50%': { boxShadow: '0 0 40px rgba(159, 122, 255, 0.6)' },
        },
        'scale-breathe': {
          '0%, 100%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.05)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
