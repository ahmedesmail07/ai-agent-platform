@echo off
echo Running AI Agent Platform Tests with Isolated Test Database...

REM Set test environment variables
set TEST_DATABASE_URL=sqlite+aiosqlite:///./test_ai_agent_platform_test.db
set OPENAI_API_KEY="TEST_OPENAI_API_KEY"
set DEBUG=True
set TESTING=True

REM Initialize test database
echo Initializing test database...
python scripts/init_test_db.py init
if errorlevel 1 (
    echo Failed to initialize test database!
    pause
    exit /b 1
)

REM Run tests with proper configuration
echo Running tests...
python -m pytest tests/ -v --tb=short --disable-warnings

REM Clean up test database
echo Cleaning up test database...
python scripts/init_test_db.py cleanup

echo.
echo Tests completed!
pause 