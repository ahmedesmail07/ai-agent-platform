# AI Agent Platform

A FastAPI-based platform for managing and orchestrating AI agents. This project provides a robust foundation for building AI agent systems with async database support, comprehensive API endpoints, and Docker containerization.

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **Async SQLAlchemy**: Asynchronous database operations with SQLite
- **Pydantic Models**: Data validation and serialization
- **Docker Support**: Containerized deployment with Python 3.10
- **RESTful API**: Complete CRUD operations for agents and chat sessions
- **OpenAI Integration**: AI-powered chat responses using GPT models
- **Voice Processing**: Speech-to-text and text-to-speech capabilities
- **Health Checks**: Built-in health monitoring
- **CORS Support**: Cross-origin resource sharing enabled
- **Comprehensive Testing**: Full test suite with pytest and mocking
- **API Documentation**: Interactive Swagger UI and Postman collection
- **Environment Configuration**: .env file support for easy configuration

## Project Structure

```
ai_agent_platform/
├── app/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   ├── base.py
│   │   └── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── agent.py
│   │   ├── session.py
│   │   └── audio.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── session.py
│   │   ├── message.py
│   │   └── voice.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── agent_service.py
│   │   ├── session_service.py
│   │   └── voice.py
│   └── routes/
│       ├── __init__.py
│       ├── agent_routes.py
│       ├── sessions.py
│       └── voice.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_agents.py
│   ├── test_sessions.py
│   ├── test_voice.py
│   └── test_health.py
├── alembic/                # Database migrations (included in git)
│   ├── env.py
│   ├── versions/
│   └── ...
├── frontend/               # React frontend (source included, build/deps excluded)
│   ├── src/
│   ├── public/
│   └── ...
├── audio_files/
├── main.py
├── requirements.txt
├── pytest.ini
├── Dockerfile
├── docker-compose.yml
├── env.example
├── README.md
└── ...
```

## Version Control and .gitignore

- The root `.gitignore` covers all backend and frontend exclusions. There is no need for a separate `frontend/.gitignore`.
- The `alembic/` directory (including all migration scripts) **must be included** in git for database versioning.
- The entire frontend source code is included, but `node_modules/`, `build/`, and environment files are excluded.

## Prerequisites

- Python 3.10+ (for local development)
- Node.js 16+ and npm (for frontend development)
- Docker (for containerized deployment)
- OpenAI API key (for AI chat and voice functionality)

## Installation

### Local Development

1. Clone the repository:

```bash
git clone <repository-url>
cd ai_agent_platform
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install backend dependencies:

```bash
pip install -r requirements.txt
```

4. Set up backend environment variables:

```bash
# Copy the example environment file
cp env.example .env

# Edit .env file with your configuration
# At minimum, set your OpenAI API key:
# OPENAI_API_KEY=your-openai-api-key-here
```

5. Run the backend application:

```bash
python main.py
```

The API will be available at `http://localhost:8000`

6. Set up and run the frontend (in a new terminal):

```bash
# Navigate to frontend directory
cd frontend

# Install frontend dependencies
npm install

# Set up frontend environment
cp env.example .env

# Start the frontend development server
npm start
```

The frontend will be available at `http://localhost:3000`

**Note**: Make sure both the backend (port 8000) and frontend (port 3000) servers are running for full functionality.

### Docker Deployment

#### Option 1: Using Docker Compose (Recommended)

1. Set up environment variables:

```bash
# Copy the example environment file
cp env.example .env

# Edit .env file with your configuration
# At minimum, set your OpenAI API key:
# OPENAI_API_KEY=your-openai-api-key-here
```

2. Build and run with Docker Compose:

```bash
docker-compose up --build
```

#### Option 2: Using Docker directly

1. Build the Docker image:

```bash
docker build -t ai-agent-platform .
```

2. Run the container:

```bash
docker run -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/audio_files:/app/audio_files \
  ai-agent-platform
```

#### Option 3: Using Docker with environment variables

```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY="your-openai-api-key" \
  -e DEBUG=False \
  -e LOG_LEVEL=info \
  ai-agent-platform
```

## Environment Configuration

The application supports configuration through environment variables or a `.env` file:

### Required Variables

- `OPENAI_API_KEY`: Your OpenAI API key for AI functionality

### Optional Variables

- `DATABASE_URL`: Database connection string (default: SQLite)
- `DEBUG`: Enable debug mode (default: False)
- `LOG_LEVEL`: Logging level (default: info)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)

### Example .env file

```bash
# Copy env.example to .env and configure
OPENAI_API_KEY=your-openai-api-key-here
DATABASE_URL=sqlite+aiosqlite:///./ai_agent_platform.db
DEBUG=False
LOG_LEVEL=info
HOST=0.0.0.0
PORT=8000
```

## API Documentation

Once the application is running, you can access:

- **Interactive API Docs (Swagger UI)**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## Postman Collection

A complete Postman collection is included for API testing:

- **File**: `AI Agent Platform.postman_collection.json`
- **Description**: Pre-configured requests for all API endpoints
- **Environment Variables**: Uses `{{baseUrl}}` variable (set to `http://localhost:8000` for local development)

### Importing the Collection

1. Open Postman
2. Click "Import" button
3. Select the `AI Agent Platform.postman_collection.json` file
4. The collection will be imported with all endpoints organized by category

### Setting up Environment Variables

1. Create a new environment in Postman
2. Add variable `baseUrl` with value `http://localhost:8000`
3. Select the environment before running requests

### Available Endpoints in Collection

- **Agents**: Create, read, update, delete agents
- **Sessions**: Create and list chat sessions
- **Messages**: Send messages and get AI responses
- **Voice**: Process voice messages with speech-to-text and text-to-speech
- **Audio**: Download generated audio files
- **Health**: Health check endpoint

## API Endpoints

### Agents

- `GET /api/v1/agents/` - List all agents
- `POST /api/v1/agents/` - Create a new agent
- `GET /api/v1/agents/{agent_id}` - Get agent by ID
- `PUT /api/v1/agents/{agent_id}` - Update agent
- `DELETE /api/v1/agents/{agent_id}` - Delete agent

### Chat Sessions

- `POST /api/v1/agents/{agent_id}/sessions` - Start new chat session
- `GET /api/v1/agents/{agent_id}/sessions` - List sessions for an agent
- `POST /api/v1/sessions/{session_id}/messages` - Send message and get AI response

### Voice Processing

- `POST /api/v1/sessions/{session_id}/voice` - Process voice message (speech-to-text → AI response → text-to-speech)
- `GET /api/v1/audio/{audio_filename}` - Download generated audio file

### Health Check

- `GET /health` - Health check endpoint

## Example Usage

### Create an Agent with OpenAI Configuration

```bash
curl -X POST "http://localhost:8000/api/v1/agents/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "ChatBot Agent",
       "description": "A conversational AI agent",
       "agent_type": "chatbot",
       "is_active": true,
       "configuration": {
         "model": "gpt-3.5-turbo",
         "system_prompt": "You are a helpful assistant.",
         "temperature": 0.7,
         "max_tokens": 1000
       },
       "capabilities": ["text_generation", "conversation"]
     }'
```

### Start a Chat Session

```bash
curl -X POST "http://localhost:8000/api/v1/agents/1/sessions"
```

### Send a Message and Get AI Response

```bash
curl -X POST "http://localhost:8000/api/v1/sessions/1/messages" \
     -H "Content-Type: application/json" \
     -d '{
       "content": "Hello, how are you today?"
     }'
```

### Process Voice Message

```bash
curl -X POST "http://localhost:8000/api/v1/sessions/1/voice" \
     -F "audio_file=@your_audio_file.wav"
```

### Download Generated Audio Response

```bash
curl -X GET "http://localhost:8000/api/v1/audio/response_1_abc123.mp3" \
     --output response.mp3
```

### List Sessions for an Agent

```bash
curl -X GET "http://localhost:8000/api/v1/agents/1/sessions"
```

## Voice Processing Features

### Supported Audio Formats

- **Input**: `.wav`, `.mp3`, `.m4a`, `.webm`
- **Output**: `.mp3` (using OpenAI TTS)

### Voice Processing Pipeline

1. **Speech-to-Text**: Uses OpenAI Whisper API to convert audio to text
2. **AI Processing**: Sends transcribed text to GPT model for response
3. **Text-to-Speech**: Converts AI response to audio using OpenAI TTS
4. **Storage**: Saves audio files and metadata to database

### Audio Metadata Storage

The system stores comprehensive metadata for each voice interaction:

- Input audio file information
- Output audio file path
- Transcription text
- TTS voice settings
- File formats and durations

## Development

### Running Tests

The project includes a comprehensive test suite with pytest:

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_agents.py

# Run tests with coverage
pytest --cov=app

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Test Structure

- **`tests/conftest.py`**: Test fixtures and configuration
- **`tests/test_agents.py`**: Agent endpoint tests
- **`tests/test_sessions.py`**: Session and message tests
- **`tests/test_voice.py`**: Voice processing tests
- **`tests/test_health.py`**: Health endpoint tests

### Test Features

- **Async Database Testing**: Isolated test database with automatic cleanup
- **OpenAI API Mocking**: Mocked responses for reliable testing
- **Fixture System**: Reusable test data and setup
- **Comprehensive Coverage**: Tests for success cases, validation, and error handling

### Code Formatting

```bash
# Install formatting tools
pip install black isort

# Format code
black .
isort .
```

### Code Quality

```bash
# Install linting tools
pip install flake8 mypy

# Run linting
flake8 .
mypy app/
```

## Environment Variables

The application uses the following environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (required for AI chat and voice functionality)
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `DEBUG`: Enable debug mode (default: False)
- `LOG_LEVEL`: Logging level (default: info)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Development Guidelines

- Write tests for all new features
- Follow the existing code style
- Update documentation as needed
- Ensure all tests pass before submitting PR
