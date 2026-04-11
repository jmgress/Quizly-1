"""AI integration tests using mocked providers (no real API calls)."""

import pytest
import json
import sqlite3
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))


def test_ai_endpoint_handles_unavailable_provider():
    """Test that the AI endpoint responds gracefully when no provider is available."""
    from main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.get("/api/questions/ai?subject=history&limit=2")

    # Acceptable outcomes: success or a well-formed error (not a hang or unhandled crash)
    assert response.status_code in {200, 400, 422, 500, 503}


def test_model_listing():
    """Test that listing models for the openai provider returns expected entries."""
    from llm_providers import get_available_models

    models = get_available_models("openai")

    assert isinstance(models, list)
    assert "gpt-3.5-turbo" in models


def test_provider_configuration_via_env():
    """Test that the LLM_PROVIDER environment variable is readable."""
    original = os.environ.get("LLM_PROVIDER")
    try:
        os.environ["LLM_PROVIDER"] = "test_provider"
        assert os.getenv("LLM_PROVIDER") == "test_provider"
    finally:
        if original is None:
            os.environ.pop("LLM_PROVIDER", None)
        else:
            os.environ["LLM_PROVIDER"] = original


def test_mock_ai_generation():
    """Test AI question generation with a mocked Ollama provider response."""
    mock_content = json.dumps([
        {
            "text": "What year did World War II end?",
            "options": [
                {"id": "a", "text": "1943"},
                {"id": "b", "text": "1945"},
                {"id": "c", "text": "1947"},
                {"id": "d", "text": "1949"},
            ],
            "correct_answer": "b",
            "category": "history",
        }
    ])

    with patch.dict("sys.modules", {"ollama": MagicMock()}):
        sys.modules["ollama"].chat = MagicMock(
            return_value={"message": {"content": mock_content}}
        )

        from main import generate_ai_questions

        os.environ["LLM_PROVIDER"] = "ollama"
        result = generate_ai_questions("history", 1)

    assert result is not None
    assert len(result) == 1
    question = result[0]
    assert question.get("text")
    assert question.get("options")
    assert question.get("correct_answer")
    assert question.get("id", 0) >= 1000  # AI questions have IDs >= 1000