import pytest
import json
import os
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Adjust the import path if your main app is structured differently
from main import app, LLM_CONFIG_FILE, get_llm_config, save_llm_config, LLMConfig

# Store original config and restore it after tests
original_config_content = None
original_env_vars = {}

@pytest.fixture(scope="session", autouse=True)
def backup_and_restore_config():
    global original_config_content
    global original_env_vars

    # Backup environment variables that might be set
    for var in ["LLM_PROVIDER", "OLLAMA_MODEL", "OPENAI_MODEL", "OPENAI_API_KEY", "OLLAMA_HOST"]:
        if var in os.environ:
            original_env_vars[var] = os.environ[var]

    # Backup config file
    if os.path.exists(LLM_CONFIG_FILE):
        with open(LLM_CONFIG_FILE, "r") as f:
            original_config_content = f.read()

    yield

    # Restore config file
    if original_config_content:
        with open(LLM_CONFIG_FILE, "w") as f:
            f.write(original_config_content)
    elif os.path.exists(LLM_CONFIG_FILE):
        os.remove(LLM_CONFIG_FILE)

    # Restore environment variables
    for var, value in original_env_vars.items():
        os.environ[var] = value
    for var in ["LLM_PROVIDER", "OLLAMA_MODEL", "OPENAI_MODEL"]: # remove if not present before
        if var not in original_env_vars and var in os.environ:
            del os.environ[var]


@pytest.fixture
def client():
    # Clean up config file before each test that uses client
    if os.path.exists(LLM_CONFIG_FILE):
        os.remove(LLM_CONFIG_FILE)
    # Ensure specific env vars are cleared if they affect default config reading
    if "LLM_PROVIDER" in os.environ: del os.environ["LLM_PROVIDER"]
    if "OLLAMA_MODEL" in os.environ: del os.environ["OLLAMA_MODEL"]
    if "OPENAI_MODEL" in os.environ: del os.environ["OPENAI_MODEL"]

    # Setup a default test config if needed, or rely on app defaults
    save_llm_config(LLMConfig(provider="ollama", model="test_ollama_model"))

    with TestClient(app) as c:
        yield c

    # Clean up again after test
    if os.path.exists(LLM_CONFIG_FILE):
        os.remove(LLM_CONFIG_FILE)

def test_get_llm_config_file_exists(client):
    # Prepare a config file
    test_config = {"provider": "test_provider", "model": "test_model_from_file"}
    with open(LLM_CONFIG_FILE, "w") as f:
        json.dump(test_config, f)

    response = client.get("/api/llm/config")
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "test_provider"
    assert data["model"] == "test_model_from_file"

def test_get_llm_config_file_not_exists_uses_defaults(client):
    # Ensure file does not exist (done by fixture, but good to be explicit)
    if os.path.exists(LLM_CONFIG_FILE):
        os.remove(LLM_CONFIG_FILE)

    # Set env vars for defaults if necessary, or rely on hardcoded defaults in get_llm_config
    os.environ["LLM_PROVIDER"] = "env_ollama"
    os.environ["OLLAMA_MODEL"] = "env_llama_default"

    response = client.get("/api/llm/config")
    assert response.status_code == 200
    data = response.json()
    # The get_llm_config now prioritizes file, then env, then hardcoded.
    # If file is removed by client fixture, it should use env vars.
    assert data["provider"] == "env_ollama"
    assert data["model"] == "env_llama_default"

    del os.environ["LLM_PROVIDER"]
    del os.environ["OLLAMA_MODEL"]


@pytest.mark.asyncio
async def test_post_llm_config_updates_file(client, mocker): # Added mocker fixture
    new_config_data = {"provider": "openai", "model": "gpt-test"}

    # Mock the health_check method of the created provider instance
    # The path to mock depends on where create_llm_provider is and what it returns.
    # Assuming create_llm_provider is called within the endpoint,
    # we mock the health_check on the class that will be instantiated.
    mock_openai_provider_instance = mocker.patch('llm_providers.openai_provider.OpenAIProvider.health_check')
    mock_openai_provider_instance.return_value = True

    # If testing with 'ollama' as provider, you'd mock OllamaProvider instead/additionally:
    # mock_ollama_provider_instance = mocker.patch('llm_providers.ollama_provider.OllamaProvider.health_check')
    # mock_ollama_provider_instance.return_value = True

    response = client.post("/api/llm/config", json=new_config_data)

    assert response.status_code == 200, f"Response content: {response.text}"
    data = response.json()
    assert data["provider"] == "openai"
    assert data["model"] == "gpt-test"

    # Verify the file was written
    with open(LLM_CONFIG_FILE, "r") as f:
        saved_config = json.load(f)
    assert saved_config["provider"] == "openai"
    assert saved_config["model"] == "gpt-test"

def test_post_llm_config_invalid_provider(client):
    new_config_data = {"provider": "unknown_provider", "model": "test_model"}
    response = client.post("/api/llm/config", json=new_config_data)
    assert response.status_code == 400 # ValueError from create_llm_provider
    assert "Unknown provider type" in response.json()["detail"]

# Test for /api/llm/health (simplified, assumes providers might not be fully functional in test env)
def test_get_llm_health_specific_provider(client):
    # Test with a provider that's likely to be "healthy" or at least exist in create_llm_provider
    # Ollama is often a default. We are not checking true health, just that endpoint works.
    response = client.get("/api/llm/health?provider_name=ollama")
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "ollama"
    assert "healthy" in data
    assert "models" in data # Should return models list, even if empty

    response = client.get("/api/llm/health?provider_name=openai")
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "openai"
    assert "healthy" in data
    assert "models" in data
    # If OPENAI_API_KEY is not set, healthy might be false. This is acceptable.

def test_get_llm_health_default_provider(client):
    # Relies on the default config being 'ollama' from the fixture
    save_llm_config(LLMConfig(provider="ollama", model="test_default_health"))
    response = client.get("/api/llm/health") # No provider_name, uses current config
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "ollama"
    assert "healthy" in data

# Test for /api/models
def test_get_models_for_provider(client):
    response = client.get("/api/models?provider=ollama")
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "ollama"
    assert isinstance(data["models"], list) # Models for Ollama might be empty if not running

    response = client.get("/api/models?provider=openai")
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "openai"
    assert isinstance(data["models"], list)
    # OpenAI should return its predefined list
    assert "gpt-4o-mini" in data["models"]

def test_get_models_missing_provider_param(client):
    response = client.get("/api/models")
    assert response.status_code == 422 # FastAPI returns 422 for missing required query params
    # The exact error message structure for validation errors can be more complex
    # For now, checking status code is primary. If detail is needed:
    # response_json = response.json()
    # assert any(err["msg"] == "Field required" and err["loc"] == ["query", "provider"] for err in response_json["detail"])
    assert "Field required" in response.text # Simpler check for now

def test_get_models_unknown_provider(client):
    response = client.get("/api/models?provider=unknown_test_provider")
    assert response.status_code == 400
    assert "Unknown provider type" in response.json()["detail"]


# Test for /api/llm/providers
def test_get_llm_providers_endpoint(client):
    response = client.get("/api/llm/providers")
    assert response.status_code == 200
    data = response.json()
    assert "current_provider" in data
    assert "current_model" in data
    assert "available_providers" in data
    assert isinstance(data["available_providers"], list)

    found_ollama = any(p["name"] == "ollama" for p in data["available_providers"])
    found_openai = any(p["name"] == "openai" for p in data["available_providers"])
    assert found_ollama
    assert found_openai

    for p_info in data["available_providers"]:
        assert "name" in p_info
        assert "healthy" in p_info
        assert "models" in p_info
        assert isinstance(p_info["models"], list)

# It might be good to also test the AI question generation endpoint
# to ensure it uses the config from llm_config.json
@pytest.mark.asyncio
async def test_ai_question_generation_uses_config_file(client):
    # Setup a specific config
    test_config = LLMConfig(provider="ollama", model="test_ai_model") # Assuming ollama can be mocked or is available
    save_llm_config(test_config)

    # Mock the actual provider's generate_questions method
    # This requires a bit more advanced patching with pytest-mock or unittest.mock
    # For simplicity, this test will currently make a real call if not mocked.
    # If Ollama is not running, this will fail or return a 503.
    # A proper test would mock 'create_llm_provider' to return a mock provider.

    # This is a placeholder for where mocking would be essential for robust testing:
    # with patch('main.create_llm_provider') as mock_create_provider:
    #     mock_provider_instance = MagicMock()
    #     mock_provider_instance.generate_questions.return_value = [
    #         {"id": 1, "text": "Test question", "options": [], "correct_answer": "a", "category": "test"}
    #     ]
    #     mock_create_provider.return_value = mock_provider_instance
    #
    #     response = client.get("/api/questions/ai?subject=testing")
    #     assert response.status_code == 200
    #     # Add more assertions based on expected behavior with mocked provider
    #     mock_create_provider.assert_called_with(provider_type="ollama", model="test_ai_model")


    # Simplified check, just that it attempts with configured provider (if not mocked)
    # This part of the test is more of an integration test as is.
    # If Ollama is not running, this will likely result in a 503 error from the endpoint.
    # To make it a unit test, mocking is necessary.
    response = client.get("/api/questions/ai?subject=testing_config_use")
    if response.status_code == 503:
        # This is an expected outcome if Ollama isn't running and not mocked
        assert f"{test_config.provider.capitalize()} question generation failed" in response.json()["detail"]
    elif response.status_code == 200:
        # This means the call succeeded, implying it used the configured provider.
        pass
    else:
        # Fail if any other status code
        assert False, f"Unexpected status code {response.status_code}: {response.text}"

    # Clean up: restore a default config or remove the test one
    save_llm_config(LLMConfig(provider="ollama", model="default_after_test"))

# Remember to install pytest and httpx:
# pip install pytest httpx
# Run with: pytest
# If your main app is not in the root, you might need to adjust PYTHONPATH
# or how you run pytest (e.g., python -m pytest)
print("Backend tests for LLM config created in backend/test_llm_config.py")
print("To run: (ensure pytest and httpx are installed)")
print("cd backend")
print("pytest")

# Note: The test_post_llm_config_updates_file and test_ai_question_generation_uses_config_file
# might require mocking for true unit testing, especially for provider health checks
# and actual question generation, to avoid external dependencies (like a running Ollama instance or OpenAI API calls).
# The provided tests are a mix of unit and integration tests.
