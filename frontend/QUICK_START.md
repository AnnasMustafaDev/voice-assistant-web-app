# Quick Start Guide - Frontend

## Setup & Run

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
```bash
# Copy example to create .env
cp .env.example .env

# Edit .env with your backend URL:
# VITE_BACKEND_URL=http://localhost:8000
```

### 3. Start Development Server
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## Integration with Backend

### Prerequisites
- Backend should be running on `http://localhost:8000` (or configured URL)
- Backend WebSocket endpoint: `ws://localhost:8000/voice/stream`

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_BACKEND_URL` | `http://localhost:8000` | Backend server URL |
| `VITE_TENANT_ID` | `demo-tenant` | Multi-tenant identifier |
| `VITE_AGENT_ID` | `receptionist-1` | Agent identifier |
| `VITE_AGENT_NAME` | `Reception Agent` | Display name for agent |

## Project Structure

```
frontend/
├── src/
│   ├── App.tsx                 # Main app component
│   ├── main.tsx                # Entry point
│   ├── components/
│   │   ├── VoiceBubble.tsx     # Voice interaction component
│   │   ├── Transcript.tsx      # Conversation display
│   │   └── StatusIndicator.tsx # Status bar
│   ├── hooks/
│   │   ├── useWebSocket.ts     # WebSocket hook
│   │   └── useMicrophone.ts    # Microphone hook
│   ├── store/
│   │   └── agentStore.ts       # Zustand state store
│   ├── utils/
│   │   ├── audio.ts            # Audio utilities
│   │   ├── websocket.ts        # WebSocket handlers
│   │   └── animations.ts       # Framer Motion variants
│   ├── types/
│   │   └── index.ts            # TypeScript types
│   └── styles/
│       └── globals.css         # Tailwind CSS
├── tailwind.config.js          # Tailwind configuration
├── postcss.config.js           # PostCSS configuration
├── tsconfig.json               # TypeScript configuration
├── vite.config.ts              # Vite configuration
├── package.json                # Dependencies
├── .env                        # Environment variables (local)
├── .env.example                # Environment template
└── README.md                   # Full documentation
```

## Development Workflow

### Start Dev Server
```bash
npm run dev
```
- Fast refresh (HMR) enabled
- TypeScript type checking
- Vite's instant feedback

### Build for Production
```bash
npm run build
```
- Creates optimized build in `dist/`
- Bundles CSS, JS with minification
- Ready for deployment

### Preview Production Build
```bash
npm run preview
```
- Serve the production build locally
- Verify optimizations

## Key Features Implemented

✅ **Voice-First UI**
- Central animated voice bubble
- 5 states: idle, listening, thinking, speaking, error
- Microphone amplitude visualization

✅ **Real-Time Communication**
- WebSocket connection to backend
- Audio streaming (user → server)
- Audio playback (server → user)
- Live transcript updates

✅ **State Management**
- Zustand store for global state
- Type-safe hooks
- DevTools support ready

✅ **Animations**
- Framer Motion for smooth animations
- State-based animation variants
- Organic easing curves
- Ripple effects during listening

✅ **Styling**
- Tailwind CSS with custom theme
- Purple gradient primary colors
- Responsive design
- Accessible color contrast

## Testing Connection

### Manual Testing
1. Open http://localhost:5173
2. Verify "Connected" status indicator (green dot)
3. Click voice bubble to start listening
4. Speak clearly
5. Wait for response

### Troubleshooting

**"Connecting..." status (not green)**
- Check backend URL in `.env`
- Ensure backend is running
- Check browser console for errors

**Microphone not working**
- Allow microphone permission in browser
- Ensure HTTPS in production
- Check if browser supports Web Audio API

**No sound playback**
- Check browser volume
- Verify backend is sending audio
- Check browser's autoplay policy

## Architecture Overview

```
┌─────────────────────────────────────────┐
│  Frontend (React + TypeScript + Vite)   │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐  │
│  │      VoiceBubble (Component)     │  │
│  │  - State animations              │  │
│  │  - Click handlers                │  │
│  └──────────────────────────────────┘  │
│                  │                      │
│  ┌───────────────┴───────────────────┐ │
│  │       useMicrophone Hook          │ │
│  │  - Audio capture                  │ │
│  │  - Amplitude analysis             │ │
│  └──────────────────────────────────┘ │
│                  │                      │
│  ┌───────────────┴───────────────────┐ │
│  │       useWebSocket Hook           │ │
│  │  - WS connection management       │ │
│  │  - Message routing                │ │
│  └──────────────────────────────────┘ │
│                  │                      │
│  ┌───────────────┴───────────────────┐ │
│  │        agentStore (Zustand)       │ │
│  │  - Global state                   │ │
│  │  - Actions                        │ │
│  └──────────────────────────────────┘ │
│                  │                      │
└──────────────────┼──────────────────────┘
                   │ WebSocket
            ┌──────┴──────┐
            │   Backend   │
            │  (FastAPI)  │
            └─────────────┘
```

## Next Steps

1. **Customize Theme**: Edit `tailwind.config.js` colors
2. **Add More Components**: Follow the component pattern
3. **Enhance Animations**: Update `utils/animations.ts`
4. **Test Integration**: Use backend API docs to test endpoints
5. **Deploy**: Build and deploy to Vercel, Netlify, or your server

## Common Tasks

### Change Agent Name
```env
VITE_AGENT_NAME=My Custom Agent
```

### Update Backend URL
```env
VITE_BACKEND_URL=https://api.example.com
```

### Customize Colors
Edit `tailwind.config.js`:
```js
colors: {
  primary: {
    500: '#your-color',
    // ...
  }
}
```

### Add New Hook
1. Create `src/hooks/useYourHook.ts`
2. Export from `src/hooks/index.ts`
3. Use in components: `import { useYourHook } from '../hooks'`

## Performance Tips

- Use React.memo for expensive components
- Lazy load components with dynamic imports
- Monitor WebSocket connection health
- Optimize audio encoding on server
- Use browser DevTools Performance tab

## Support

- Check [README.md](./README.md) for full documentation
- Review component source code for examples
- Check browser console for errors
- Ensure backend API is running and accessible
