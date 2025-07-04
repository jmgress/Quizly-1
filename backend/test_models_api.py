"""Tests for the new models API endpoints."""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_models_endpoint():
    """Test the models endpoint returns proper structure"""
    response = client.get("/api/models")
    assert response.status_code == 200
    
    data = response.json()
    assert "models" in data
    assert "default" in data
    assert isinstance(data["models"], dict)
    assert isinstance(data["default"], dict)
    
    # Check default models are defined
    assert "openai" in data["default"]
    assert "ollama" in data["default"]
    assert data["default"]["openai"] == "gpt-4o-mini"
    assert data["default"]["ollama"] == "llama3.2"

def test_ai_questions_with_model_parameter():
    """Test AI questions endpoint accepts model parameter"""
    # Test that the endpoint accepts the new model parameter without errors
    # Note: This will fail without proper LLM setup, but should validate parameter acceptance
    response = client.get("/api/questions/ai?subject=test&model=gpt-4o-mini&provider_type=openai")
    
    # Should get 503 due to missing API key, but not 422 (validation error)
    assert response.status_code == 503
    assert "OpenAI" in response.json()["detail"]

def test_ai_questions_with_ollama_model():
    """Test AI questions endpoint with Ollama model parameter"""
    response = client.get("/api/questions/ai?subject=test&model=llama3.2&provider_type=ollama")
    
    # Should get 503 due to Ollama not running, but not 422 (validation error)
    assert response.status_code == 503
    assert "Ollama" in response.json()["detail"]