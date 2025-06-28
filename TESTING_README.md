# Testing Guide for AI Agent Platform

This guide explains how to run the comprehensive test suite for the AI Agent Platform with a completely isolated test database.

## Test Database Isolation

The test suite uses a completely separate test database to ensure:

- No interference with production data
- Safe test execution
- Clean test environment for each run
- Parallel test execution capability

### Test Database Configuration

- Test Database File: `test_ai_agent_platform_test.db`
- Environment Variable: `TEST_DATABASE_URL`
- Location: Project root directory
- Type: SQLite (in-memory/file-based)

## Version Control and .gitignore

- The root `.gitignore` covers all test database, cache, and environment file exclusions.
- The `alembic/` directory (with migration scripts) is included in git for database versioning.

## Prerequisites

- Python 3.8+ with virtual environment activated
- All dependencies installed (`pip install -r requirements.txt`)
- Test database URL configured

## Quick Start

### Option 1: Using the provided script (Windows)

```bash
run-tests.bat
```

This script will:

1. Set up the isolated test database
2. Run all tests
3. Clean up the test database

### Option 2: Manual setup

1. **Set environment variables:**

   **Windows PowerShell:**

   ```powershell
   $env:TEST_DATABASE_URL="sqlite+aiosqlite:///./test_ai_agent_platform_test.db"
   $env:OPENAI_API_KEY="sk-test-key-for-testing-only"
   $env:DEBUG="True"
   $env:TESTING="True"
   ```

   **Windows Command Prompt:**

   ```cmd
   set TEST_DATABASE_URL=sqlite+aiosqlite:///./test_ai_agent_platform_test.db
   set OPENAI_API_KEY=sk-test-key-for-testing-only
   set DEBUG=True
   set TESTING=True
   ```

2. **Initialize test database:**

   ```bash
   python scripts/init_test_db.py init
   ```

3. **Run tests:**

   ```bash
   python -m pytest tests/ -v
   ```

4. **Clean up test database:**
   ```bash
   python scripts/init_test_db.py cleanup
   ```

## Test Database Management

### Initialize Test Database

```bash
python scripts/init_test_db.py init
```

### Reset Test Database

```bash
python scripts/init_test_db.py reset
```

### Clean Up Test Database

```bash
python scripts/init_test_db.py cleanup
```

## Running Specific Tests

### Run all tests

```bash
python -m pytest tests/ -v
```

### Run specific test file

```bash
python -m pytest tests/test_agents.py -v
```

### Run specific test function

```bash
python -m pytest tests/test_agents.py::test_create_agent -v
```

### Run tests with coverage

```bash
python -m pytest tests/ --cov=app --cov-report=html
```

### Run tests in parallel

```bash
python -m pytest tests/ -n auto
```

## Test Categories

### Unit Tests

- **Location**: `tests/test_*.py`
- **Purpose**: Test individual functions and classes
- **Database**: Uses isolated test database
- **Speed**: Fast execution

### Integration Tests

- **Purpose**: Test API endpoints and database interactions
- **Database**: Uses isolated test database
- **Speed**: Medium execution

### Health Check Tests

- **File**: `tests/test_health.py`
- **Purpose**: Verify API health and basic functionality

## Test Fixtures

The test suite provides several fixtures for common testing scenarios:

- `client`: HTTP test client with test database
- `db_session`: Database session for test database
- `sample_agent`: Pre-created agent for testing
- `sample_session`: Pre-created chat session
- `sample_message`: Pre-created message
- `mock_openai`: Mocked OpenAI API responses

## Environment Variables

| Variable            | Description                     | Test Value                                             |
| ------------------- | ------------------------------- | ------------------------------------------------------ |
| `TEST_DATABASE_URL` | Test database connection string | `sqlite+aiosqlite:///./test_ai_agent_platform_test.db` |
| `OPENAI_API_KEY`    | OpenAI API key for testing      | `sk-test-key-for-testing-only`                         |
| `DEBUG`             | Enable debug mode               | `True`                                                 |
| `TESTING`           | Enable testing mode             | `True`                                                 |

## Safety Features

### Database Isolation

- ✅ Separate test database file
- ✅ Automatic cleanup after tests
- ✅ No access to production database
- ✅ Validation to prevent production database usage

### Environment Validation

- ✅ Checks for required environment variables
- ✅ Validates test database URL format
- ✅ Prevents accidental production database usage

### Cleanup

- ✅ Automatic test database cleanup
- ✅ Rollback of uncommitted changes
- ✅ Removal of test files

## Troubleshooting

### Test Database Issues

**Error: "TEST_DATABASE_URL environment variable is not set"**

```bash
# Set the environment variable
set TEST_DATABASE_URL=sqlite+aiosqlite:///./test_ai_agent_platform_test.db
```

**Error: "TEST_DATABASE_URL points to production database"**

```bash
# Use a separate test database file
set TEST_DATABASE_URL=sqlite+aiosqlite:///./test_ai_agent_platform_test.db
```

### Async Fixture Warnings

The test suite uses `pytest-asyncio` for async testing. If you see warnings about async fixtures, ensure you have the latest version:

```bash
pip install --upgrade pytest-asyncio
```

### Database Lock Issues

If you encounter database lock issues, try:

```bash
# Clean up any existing test database
python scripts/init_test_db.py cleanup
# Reinitialize
python scripts/init_test_db.py init
```

## Continuous Integration

For CI/CD pipelines, ensure:

1. Set `TEST_DATABASE_URL` environment variable
2. Use in-memory SQLite for faster execution
3. Run tests in isolated environment
4. Clean up after test execution

Example CI configuration:

```yaml
env:
  TEST_DATABASE_URL: sqlite+aiosqlite:///:memory:
  OPENAI_API_KEY: sk-test-key-for-testing-only
  TESTING: true
```

## Test Structure

```
tests/
├── conftest.py          # Test configuration and fixtures
├── test_agents.py       # Agent management tests
├── test_health.py       # Health check and root endpoint tests
├── test_sessions.py     # Session and message tests
└── test_voice.py        # Voice processing tests
```

## Test Categories

### 1. Agent Tests (`test_agents.py`)

- Create, read, update, delete agents
- Agent validation
- Pagination

### 2. Health Tests (`test_health.py`)

- Health check endpoint
- Root endpoint

### 3. Session Tests (`test_sessions.py`)

- Session creation and management
- Message sending and receiving
- OpenAI integration

### 4. Voice Tests (`test_voice.py`)

- Voice message processing
- Audio file handling
- Transcription and TTS

## Running Specific Tests

### Run a specific test file:

```bash
python -m pytest tests/test_health.py -v
```

### Run a specific test class:

```bash
python -m pytest tests/test_agents.py::TestAgents -v
```

### Run a specific test method:

```bash
python -m pytest tests/test_agents.py::TestAgents::test_create_agent -v
```

### Run tests with specific markers:

```bash
python -m pytest -m "not slow" -v
```

## Test Configuration

### Environment Variables

| Variable            | Description                     | Default  |
| ------------------- | ------------------------------- | -------- |
| `TEST_DATABASE_URL` | Test database connection string | Required |
| `OPENAI_API_KEY`    | OpenAI API key for testing      | Required |
| `DEBUG`             | Enable debug mode               | `True`   |

### Pytest Configuration (`pytest.ini`)

- **Test paths**: `tests/`
- **Python files**: `test_*.py`
- **Asyncio mode**: `auto`
- **Verbose output**: Enabled
- **Warning suppression**: Enabled

## Test Fixtures

The test suite uses several fixtures defined in `conftest.py`:

- `test_db_setup`: Database setup and teardown
- `db_session`: Database session for each test
- `client`: HTTP test client with database override
- `mock_openai`: Mocked OpenAI API responses
- `sample_agent`: Pre-created test agent
- `sample_session`: Pre-created test session
- `sample_message`: Pre-created test message
- `sample_audio_file`: Test audio file

## Common Issues and Solutions

### 1. Database Connection Issues

**Error**: `TEST_DATABASE_URL environment variable is not set`

**Solution**: Set the environment variable:

```bash
set TEST_DATABASE_URL=sqlite+aiosqlite:///./test_ai_agent_platform_test.db
```

### 2. Async Fixture Warnings

**Error**: Async fixture warnings

**Solution**: The fixtures are properly configured with `@pytest_asyncio.fixture`. These warnings are informational and don't affect test execution.

### 3. OpenAI API Errors

**Error**: OpenAI API connection issues

**Solution**: Tests use mocked OpenAI responses, so real API calls are not made during testing.

### 4. Import Errors

**Error**: Module not found

**Solution**: Ensure you're in the project root directory and the virtual environment is activated.

## Test Database

- **Type**: SQLite (in-memory for testing)
- **File**: `test_ai_agent_platform.db` (created automatically)
- **Cleanup**: Database is recreated for each test session

## Mocking

The test suite uses extensive mocking to avoid external dependencies:

- **OpenAI API**: Mocked responses for chat, speech, and transcription
- **File System**: In-memory file operations
- **Database**: Isolated test database

## Coverage

To run tests with coverage:

```bash
pip install pytest-cov
python -m pytest tests/ --cov=app --cov-report=html
```

This will generate a coverage report in `htmlcov/index.html`.

## Best Practices

1. **Isolation**: Each test is isolated and doesn't depend on others
2. **Cleanup**: Database is cleaned up after each test session
3. **Mocking**: External dependencies are mocked
4. **Async Support**: Proper async/await handling
5. **Error Handling**: Tests verify both success and error cases

## Troubleshooting

### Tests not running

- Check Python environment and dependencies
- Verify environment variables are set
- Ensure you're in the project root directory

### Database errors

- Check `TEST_DATABASE_URL` format
- Ensure SQLite is available
- Check file permissions

### Import errors

- Activate virtual environment
- Install dependencies: `pip install -r requirements.txt`
- Check Python path

### Performance issues

- Use `-x` flag to stop on first failure
- Use `-k` flag to run specific tests
- Use `--tb=short` for shorter tracebacks
