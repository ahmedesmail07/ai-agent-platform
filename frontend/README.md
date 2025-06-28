# AI Agent Platform Frontend

A modern React + TypeScript frontend for the AI Agent Platform, featuring a beautiful chat interface with voice support.

## Version Control and .gitignore

- The root `.gitignore` in the project covers all frontend exclusions (such as `node_modules/`, `build/`, and environment files).
- The entire frontend source code (everything in `src/`, `public/`, etc.) is always included in git.
- There is no need for a separate `.gitignore` in the frontend directory.

## Features

- **Agent Management**: Create, edit, and delete AI agents with full configuration
- **Session Management**: Start new chat sessions and switch between existing ones
- **Real-time Chat**: Send text messages and receive AI responses
- **Voice Support**: Record and send voice messages using MediaRecorder API
- **Audio Playback**: Play AI-generated audio responses
- **Responsive Design**: Modern UI built with TailwindCSS
- **TypeScript**: Full type safety throughout the application

## Tech Stack

- **React 18** with TypeScript
- **TailwindCSS** for styling
- **Axios** for API communication
- **Lucide React** for icons
- **MediaRecorder API** for voice recording

## Project Structure

```
src/
├── components/          # React components
│   ├── AgentList.tsx   # Left sidebar with agent management
│   ├── SessionSelector.tsx # Top section with session selection
│   ├── ChatView.tsx    # Center chat area
│   └── ChatInput.tsx   # Bottom input area with voice support
├── hooks/              # Custom React hooks
│   └── useVoiceRecorder.ts # Voice recording hook
├── services/           # API services
│   └── api.ts         # Backend API communication
├── types/              # TypeScript type definitions
│   └── api.ts         # API response types
└── App.tsx            # Main application component
```

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- Backend API running (see main README)

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create environment file:
```bash
cp .env.example .env
```

4. Configure environment variables:
```bash
# Backend API URL
REACT_APP_API_URL=http://localhost:3000/api/v1
```

### Development

Start the development server:
```bash
npm start
```

The application will be available at `http://localhost:3000`

### Building for Production

Build the application:
```bash
npm run build
```

The built files will be in the `build/` directory.

## Usage

### Agent Management

1. **Create Agent**: Click the "+" button in the left sidebar
2. **Edit Agent**: Click the edit icon on any agent card
3. **Delete Agent**: Click the trash icon on any agent card
4. **Select Agent**: Click on an agent to start chatting

### Chat Sessions

1. **Start New Session**: Click "New Session" in the top bar
2. **Switch Sessions**: Use the session dropdown in the top bar
3. **View Session History**: Sessions are listed with timestamps

### Messaging

1. **Text Messages**: Type in the input box and press Enter or click Send
2. **Voice Messages**: Click the microphone button to record
3. **Audio Playback**: Click "Play Audio" on AI responses with voice

### Voice Recording

- Click the microphone button to start recording
- Click the stop button to finish recording
- The audio will be automatically sent to the AI
- AI responses include both text and audio

## API Integration

The frontend communicates with the backend through the following endpoints:

- `GET /agents/` - List all agents
- `POST /agents/` - Create new agent
- `PUT /agents/{id}` - Update agent
- `DELETE /agents/{id}` - Delete agent
- `GET /agents/{id}/sessions` - List sessions for agent
- `POST /agents/{id}/sessions` - Create new session
- `POST /sessions/{id}/messages` - Send text message
- `POST /sessions/{id}/voice` - Send voice message
- `GET /audio/{filename}` - Download audio file

## Voice Recording Features

### MediaRecorder API

The application uses the MediaRecorder API for voice recording:

- **Format**: WebM with Opus codec
- **Quality**: High-quality audio capture
- **Browser Support**: Modern browsers with MediaRecorder support
- **Fallback**: Graceful error handling for unsupported browsers

### Recording States

- **Idle**: Ready to start recording
- **Recording**: Actively capturing audio
- **Processing**: Converting and sending audio
- **Error**: Display error message if recording fails

## Styling

The application uses TailwindCSS with a custom color scheme:

- **Primary Colors**: Blue palette for buttons and highlights
- **Gray Scale**: Neutral colors for backgrounds and text
- **Status Colors**: Red for errors, green for success
- **Responsive**: Mobile-friendly design

## Development Notes

### State Management

The application uses React's built-in state management:

- **Local State**: Component-specific state with useState
- **Props**: Data flow between components
- **Effects**: Side effects with useEffect

### Error Handling

- **API Errors**: Displayed in toast notifications
- **Voice Errors**: Shown in the input area
- **Network Errors**: Graceful fallbacks

### Performance

- **Lazy Loading**: Components load as needed
- **Memoization**: Optimized re-renders
- **Audio Optimization**: Efficient audio handling

## Browser Support

- **Chrome**: Full support
- **Firefox**: Full support
- **Safari**: Full support
- **Edge**: Full support

### Voice Recording Support

- **Chrome**: ✅ Full support
- **Firefox**: ✅ Full support
- **Safari**: ⚠️ Limited support (may require HTTPS)
- **Edge**: ✅ Full support

## Troubleshooting

### Common Issues

1. **Voice Recording Not Working**
   - Check browser permissions for microphone access
   - Ensure HTTPS in production (required for MediaRecorder)
   - Try refreshing the page

2. **API Connection Errors**
   - Verify backend is running on correct port
   - Check CORS configuration
   - Ensure environment variables are set

3. **Audio Playback Issues**
   - Check browser audio permissions
   - Verify audio file format support
   - Clear browser cache

### Development Tips

- Use browser dev tools to debug API calls
- Check console for error messages
- Test voice recording in incognito mode
- Verify environment variables are loaded

## Contributing

1. Follow the existing code style
2. Add TypeScript types for new features
3. Test voice recording functionality
4. Update documentation as needed

## License

This project is licensed under the MIT License.
