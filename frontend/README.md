# Reception Voice Agent - Frontend

A modern, voice-first React application for real-time conversation with AI agents. Built with TypeScript, Vite, Tailwind CSS, and Framer Motion.

## Features

- **Voice-First Interface**: Central voice bubble with state-based animations
- **Real-Time Transcription**: Live transcript display with speaker identification
- **WebSocket Integration**: Real-time bidirectional communication with backend
- **Responsive Design**: Beautiful, professional UI with smooth animations
- **Audio Visualization**: Microphone amplitude visualization during listening
- **Error Handling**: Graceful error states and recovery mechanisms

## Tech Stack

- **React 18+**: Modern UI framework with hooks
- **TypeScript**: Type-safe development
- **Vite**: Lightning-fast build tool
- **Tailwind CSS**: Utility-first CSS framework with custom design tokens
- **Framer Motion**: Production-ready animation library
- **Zustand**: Lightweight state management
- **Web Audio API**: Microphone input and audio analysis

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Update .env with your backend URL
# VITE_BACKEND_URL=http://your-backend-url:8000
```

### Development

```bash
# Start dev server
npm run dev

# The app will be available at http://localhost:5173
```

### Building

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── components/          # React components
│   ├── VoiceBubble.tsx  # Main voice interaction component
│   ├── Transcript.tsx   # Conversation transcript display
│   └── StatusIndicator.tsx
├── hooks/              # Custom React hooks
│   ├── useWebSocket.ts # WebSocket connection management
│   └── useMicrophone.ts # Microphone input handling
├── store/              # Zustand state management
│   └── agentStore.ts   # Global agent state
├── utils/              # Utility functions
│   ├── audio.ts        # Audio encoding/decoding
│   ├── websocket.ts    # WebSocket message handlers
│   └── animations.ts   # Framer Motion variants
├── types/              # TypeScript interfaces
│   └── index.ts        # Global type definitions
├── styles/             # CSS files
│   └── globals.css     # Tailwind CSS setup
├── App.tsx             # Main application component
└── main.tsx            # Entry point
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
VITE_BACKEND_URL=http://localhost:8000
VITE_TENANT_ID=demo-tenant
VITE_AGENT_ID=receptionist-1
VITE_AGENT_NAME=Reception Agent
```

## Component API

### VoiceBubble

Core voice interaction component with state-based animations.

```tsx
<VoiceBubble 
  onClick={handleClick}
  onStateChange={(state) => console.log(state)}
/>
```

**States**: `idle`, `listening`, `thinking`, `speaking`, `error`

### Transcript

Displays conversation history with role-based styling.

```tsx
<Transcript />
```

### StatusIndicator

Shows connection status and agent information.

```tsx
<StatusIndicator />
```

## Hooks

### useWebSocket

Manages WebSocket connection to the backend.

```tsx
const { send, disconnect, isConnected } = useWebSocket({
  url: 'ws://localhost:8000/voice/stream',
  onConnect: () => console.log('connected'),
  onDisconnect: () => console.log('disconnected'),
});

// Send a message
send({ event: 'audio_chunk', data: 'base64-encoded-audio' });
```

### useMicrophone

Handles microphone access and amplitude analysis.

```tsx
const { startMicrophone, stopMicrophone, isInitialized } = useMicrophone();

await startMicrophone();
// Microphone amplitude is automatically updated in Zustand store
```

## State Management

### useAgentStore

Zustand store for managing application state.

```tsx
const {
  agentState,           // 'idle' | 'listening' | 'thinking' | 'speaking' | 'error'
  transcript,           // Array of transcript items
  isConnected,          // WebSocket connection status
  error,                // Error message
  microphoneAmplitude,  // 0-1 normalized amplitude
  setAgentState,        // Update agent state
  addTranscriptItem,    // Add transcript entry
  setError,             // Set error message
  // ... other actions
} = useAgentStore();
```

## WebSocket Message Format

### Client → Server

```json
{
  "event": "audio_chunk",
  "data": "base64-encoded-wav-audio"
}
```

### Server → Client

```json
{
  "event": "transcript_partial",
  "text": "user's spoken text"
}
```

```json
{
  "event": "audio_response",
  "data": "base64-encoded-wav-audio"
}
```

```json
{
  "event": "status",
  "status": "thinking"
}
```

## Animation System

Animations use Framer Motion with custom variants for each state. Key animation parameters:

- **VoiceBubble**: Scale, opacity, and glow effects per state
- **InnerCircle**: Responsive to microphone amplitude during listening
- **Listening Ripple**: Expanding circle effect during active listening
- **Transcript**: Smooth fade-in animations for new messages

All animations use ease-in-out timing for organic motion.

## Styling

### Custom Tailwind Tokens

The project includes custom Tailwind CSS configuration with:

- Purple gradient color scheme (primary brand color)
- Slate neutral colors (secondary)
- Custom animations (pulse-soft, glow, scale-breathe)
- Responsive spacing and typography

Edit `tailwind.config.js` to customize the design tokens.

## Deployment

### Build for Production

```bash
npm run build
```

This creates an optimized production build in the `dist/` directory.

### Deploy to Vercel

```bash
npm install -g vercel
vercel
```

### Deploy to Netlify

```bash
npm run build
# Drag and drop dist/ to Netlify
```

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers with Web Audio API support

## Troubleshooting

### Microphone not working

1. Check browser permissions for microphone access
2. Ensure HTTPS in production (Web Audio API requires secure context)
3. Verify `getUserMedia` is supported in your browser

### WebSocket connection fails

1. Check backend URL in `.env` file
2. Ensure backend is running and WebSocket endpoint is available
3. Check CORS policy if frontend and backend are on different domains
4. For HTTPS frontend, ensure backend also uses WSS (secure WebSocket)

### Build errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

## Performance Optimization

- Code splitting via Vite's dynamic imports
- Image optimization with WebP format
- CSS purging with Tailwind CSS
- Audio compression before transmission
- Debounced state updates for microphone amplitude

## Accessibility

- Semantic HTML structure
- ARIA labels for interactive elements
- Keyboard navigation support
- Color contrast meets WCAG AA standards
- Screen reader friendly transcript display

## Development Tools

- **ESLint**: Linting configuration (extend in `.eslintrc`)
- **TypeScript**: Type checking
- **Vite**: HMR for instant feedback

## License

MIT

## Support

For issues and questions, refer to the backend API documentation or contact the development team.
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
