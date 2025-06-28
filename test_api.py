import requests

# Test data for creating an agent
agent_data = {
    "name": "Test Agent",
    "description": "A test agent for development",
    "agent_type": "chatbot",
    "is_active": True,
    "configuration": {
        "model": "gpt-3.5-turbo",
        "system_prompt": "You are a helpful assistant.",
        "temperature": 0.7,
        "max_tokens": 1000,
    },
    "capabilities": {"text_generation": True, "conversation": True},
}

# Test creating an agent
response = requests.post("http://localhost:8000/api/v1/agents/", json=agent_data)
print(f"Status code: {response.status_code}")
print(f"Response: {response.json()}")

# Test getting agents
response = requests.get("http://localhost:8000/api/v1/agents/")
print(f"Status code: {response.status_code}")
print(f"Response: {response.json()}")
