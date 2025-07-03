#!/usr/bin/env python3

import os
import sys
from unittest.mock import patch, MagicMock
import pytest # Using pytest for better test structure and fixtures
from fastapi import HTTPException

# Add the backend directory to Python path to allow direct import of main
# This assumes test_ai_integration.py is in backend/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Modules to be tested
from main import generate_ai_questions, get_questions # get_questions for test_category_filtering
from backend.llm_providers import (
    OllamaProvider, OpenAIProvider,
    LLMConnectionError, LLMAPIError, LLMProviderError,
    get_llm_provider as actual_get_llm_provider # So we can test the actual factory
)

# Sample valid question structure from provider
SAMPLE_PROVIDER_QUESTION = {
    "text": "What is the capital of Mocktania?",
    "options": [
        {"id": "a", "text": "Mockville"},
        {"id": "b", "text": "Testburg"},
        {"id": "c", "text": "Mock City"},
        {"id": "d", "text": "Fakeopolis"}
    ],
    "correct_answer": "c",
    "category": "mocktania"
}

# --- Tests for generate_ai_questions endpoint ---

def test_generate_ai_questions_success_ollama():
    """Test successful AI question generation using a mocked Ollama provider."""
    print("\nTesting AI generation with mocked OllamaProvider...")
    mock_provider = MagicMock(spec=OllamaProvider)
    mock_provider.generate_questions.return_value = [SAMPLE_PROVIDER_QUESTION]

    with patch('backend.main.get_llm_provider', return_value=mock_provider) as mock_get_provider:
        result = generate_ai_questions("mocktania", 1)

        mock_get_provider.assert_called_once()
        mock_provider.generate_questions.assert_called_once_with(subject="mocktania", limit=1)

        assert len(result) == 1
        question = result[0]
        assert question["text"] == SAMPLE_PROVIDER_QUESTION["text"]
        assert question["options"] == SAMPLE_PROVIDER_QUESTION["options"]
        assert question["correct_answer"] == SAMPLE_PROVIDER_QUESTION["correct_answer"]
        assert question["category"] == SAMPLE_PROVIDER_QUESTION["category"]
        assert question["id"] == 1000 # Check temporary ID assignment
        print(f"✅ Mocked OllamaProvider generation test passed! Question: {question['text']}")

def test_generate_ai_questions_success_openai():
    """Test successful AI question generation using a mocked OpenAI provider."""
    print("\nTesting AI generation with mocked OpenAIProvider...")
    mock_provider = MagicMock(spec=OpenAIProvider)
    mock_provider.generate_questions.return_value = [SAMPLE_PROVIDER_QUESTION]

    with patch('backend.main.get_llm_provider', return_value=mock_provider) as mock_get_provider:
        # We don't need to set env vars for LLM_PROVIDER here because get_llm_provider is mocked
        result = generate_ai_questions("mocktania", 1)

        mock_get_provider.assert_called_once()
        mock_provider.generate_questions.assert_called_once_with(subject="mocktania", limit=1)

        assert len(result) == 1
        question = result[0]
        assert question["text"] == SAMPLE_PROVIDER_QUESTION["text"]
        assert question["id"] >= 1000
        print(f"✅ Mocked OpenAIProvider generation test passed! Question: {question['text']}")

def test_generate_ai_questions_provider_returns_no_questions():
    """Test when the provider returns an empty list or None."""
    print("\nTesting AI generation when provider returns no questions...")
    mock_provider = MagicMock()
    mock_provider.generate_questions.return_value = [] # Simulate provider returning empty list

    with patch('backend.main.get_llm_provider', return_value=mock_provider):
        with pytest.raises(HTTPException) as exc_info:
            generate_ai_questions("empty_subject", 1)
        assert exc_info.value.status_code == 503 # As per current error handling in main.py
        assert "AI provider returned no valid questions" in exc_info.value.detail
        print(f"✅ Test for provider returning no questions passed (HTTP 503).")

    mock_provider.generate_questions.return_value = None # Simulate provider returning None
    with patch('backend.main.get_llm_provider', return_value=mock_provider):
        with pytest.raises(HTTPException) as exc_info:
            generate_ai_questions("none_subject", 1)
        assert exc_info.value.status_code == 503
        assert "AI provider returned no valid questions" in exc_info.value.detail
        print(f"✅ Test for provider returning None passed (HTTP 503).")


def test_generate_ai_questions_llm_connection_error():
    """Test handling of LLMConnectionError from provider."""
    print("\nTesting LLMConnectionError handling...")
    mock_provider = MagicMock()
    mock_provider.generate_questions.side_effect = LLMConnectionError("Test connection error")

    with patch('backend.main.get_llm_provider', return_value=mock_provider):
        with pytest.raises(HTTPException) as exc_info:
            generate_ai_questions("subject", 1)
        assert exc_info.value.status_code == 503
        assert "AI service connection error: Test connection error" in exc_info.value.detail
        print(f"✅ LLMConnectionError handling test passed (HTTP 503).")

def test_generate_ai_questions_llm_api_error():
    """Test handling of LLMAPIError from provider."""
    print("\nTesting LLMAPIError handling...")
    mock_provider = MagicMock()
    mock_provider.generate_questions.side_effect = LLMAPIError("Test API error")

    with patch('backend.main.get_llm_provider', return_value=mock_provider):
        with pytest.raises(HTTPException) as exc_info:
            generate_ai_questions("subject", 1)
        assert exc_info.value.status_code == 502
        assert "AI service API error: Test API error" in exc_info.value.detail
        print(f"✅ LLMAPIError handling test passed (HTTP 502).")

def test_generate_ai_questions_llm_provider_error():
    """Test handling of a generic LLMProviderError."""
    print("\nTesting LLMProviderError handling...")
    mock_provider = MagicMock()
    mock_provider.generate_questions.side_effect = LLMProviderError("Test generic provider error")

    with patch('backend.main.get_llm_provider', return_value=mock_provider):
        with pytest.raises(HTTPException) as exc_info:
            generate_ai_questions("subject", 1)
        assert exc_info.value.status_code == 500 # General provider error
        assert "AI service provider error: Test generic provider error" in exc_info.value.detail
        print(f"✅ LLMProviderError handling test passed (HTTP 500).")

def test_generate_ai_questions_unexpected_error():
    """Test handling of an unexpected error during generation."""
    print("\nTesting unexpected error handling...")
    mock_provider = MagicMock()
    mock_provider.generate_questions.side_effect = Exception("Highly unexpected error")

    with patch('backend.main.get_llm_provider', return_value=mock_provider):
        with pytest.raises(HTTPException) as exc_info:
            generate_ai_questions("subject", 1)
        assert exc_info.value.status_code == 500
        assert "An unexpected error occurred" in exc_info.value.detail
        print(f"✅ Unexpected error handling test passed (HTTP 500).")


# --- Tests for the get_llm_provider factory function ---
# These tests will call the actual factory function from llm_providers.py

@patch.dict(os.environ, {}, clear=True) # Start with a clean environment
def test_get_llm_provider_defaults_to_ollama():
    """Test factory defaults to OllamaProvider if LLM_PROVIDER is not set."""
    print("\nTesting provider factory default...")
    # Unset relevant env vars
    if "LLM_PROVIDER" in os.environ: del os.environ["LLM_PROVIDER"]
    if "OLLAMA_API_HOST" in os.environ: del os.environ["OLLAMA_API_HOST"]
    if "OLLAMA_MODEL" in os.environ: del os.environ["OLLAMA_MODEL"]

    provider = actual_get_llm_provider()
    assert isinstance(provider, OllamaProvider)
    assert provider.host == "http://localhost:11434" # Default host
    assert provider.model == "mistral" # Default model
    print(f"✅ Factory default to OllamaProvider test passed.")

@patch.dict(os.environ, {"LLM_PROVIDER": "ollama", "OLLAMA_API_HOST": "http://customhost:1234", "OLLAMA_MODEL": "custommodel"})
def test_get_llm_provider_ollama_with_env_vars():
    """Test factory configures OllamaProvider from environment variables."""
    print("\nTesting factory OllamaProvider with env vars...")
    provider = actual_get_llm_provider()
    assert isinstance(provider, OllamaProvider)
    assert provider.host == "http://customhost:1234"
    assert provider.model == "custommodel"
    print(f"✅ Factory OllamaProvider with env vars test passed.")

@patch.dict(os.environ, {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "test_key", "OPENAI_MODEL": "gpt-custom"})
def test_get_llm_provider_openai_with_env_vars():
    """Test factory configures OpenAIProvider from environment variables."""
    print("\nTesting factory OpenAIProvider with env vars...")
    # Mock the OpenAI client import within the OpenAIProvider constructor for this test
    with patch('backend.llm_providers.openai.OpenAI') as mock_openai_client:
        provider = actual_get_llm_provider()
        assert isinstance(provider, OpenAIProvider)
        assert provider.model == "gpt-custom"
        # Check if OpenAI client was called with the key
        mock_openai_client.assert_called_once_with(api_key="test_key")
        print(f"✅ Factory OpenAIProvider with env vars test passed.")

@patch.dict(os.environ, {"LLM_PROVIDER": "openai"}) # OPENAI_API_KEY is missing
def test_get_llm_provider_openai_missing_api_key():
    """Test factory raises ValueError for OpenAIProvider if API key is missing."""
    print("\nTesting factory OpenAIProvider missing API key...")
    # Ensure OPENAI_API_KEY is not set for this test
    if "OPENAI_API_KEY" in os.environ: del os.environ["OPENAI_API_KEY"]
    
    with pytest.raises(ValueError) as exc_info:
        actual_get_llm_provider()
    assert "OPENAI_API_KEY is required" in str(exc_info.value)
    print(f"✅ Factory OpenAIProvider missing API key test passed (ValueError).")

@patch.dict(os.environ, {"LLM_PROVIDER": "unknown_provider"})
def test_get_llm_provider_invalid_provider_defaults_to_ollama():
    """Test factory defaults to OllamaProvider if LLM_PROVIDER is invalid."""
    print("\nTesting factory invalid provider name...")
    provider = actual_get_llm_provider()
    assert isinstance(provider, OllamaProvider)
    # Should use default Ollama settings
    assert provider.host == "http://localhost:11434"
    assert provider.model == "mistral"
    print(f"✅ Factory invalid provider (defaults to Ollama) test passed.")

# --- Test for category filtering (existing test, kept for coverage) ---
def test_category_filtering():
    """Test that category filtering works with database questions"""
    # This test is for the get_questions endpoint, not AI, but was in the original file.
    # It requires a database setup or mocking. For now, assume it passes or mock DB.
    # To make it runnable without a live DB, we'd need to mock sqlite3.connect
    print("\nTesting category filtering (DB-dependent)...")
    
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    # Sample data: (id, text, options_json, correct_answer, category)
    mock_cursor.fetchall.return_value = [
        (1, "Geo Q1", '[{"id":"a","text":"OptA"}]', "a", "geography"),
        (2, "Geo Q2", '[{"id":"b","text":"OptB"}]', "b", "geography")
    ]

    with patch('sqlite3.connect', return_value=mock_conn):
        try:
            geography_questions = get_questions(category="geography", limit=2)
            if geography_questions and len(geography_questions) == 2:
                all_geography = all(q.get("category") == "geography" for q in geography_questions)
                if all_geography:
                    print("✅ Category filtering test passed (mocked DB)!")
                else:
                    print("❌ Category filtering test failed - not all questions are geography (mocked DB)")
                    assert False, "Not all questions were geography"
            else:
                print(f"❌ Category filtering test failed - incorrect number of questions returned (mocked DB), got {len(geography_questions)}")
                assert False, "Incorrect number of questions"
        except Exception as e:
            print(f"❌ Category filtering test failed with exception: {e}")
            assert False, f"Test failed with exception: {e}"


# --- Main execution for running tests directly (optional with pytest) ---
if __name__ == "__main__":
    print("🧪 Testing AI Integration and Provider Features (using pytest conventions)\n")
    # Pytest will discover and run tests automatically if you run `pytest` in the terminal
    # This block is mostly for if you execute this file directly like `python backend/test_ai_integration.py`
    # For more robust testing, use the pytest CLI.
    
    # Example of how you might manually call tests if not using pytest runner:
    # test_generate_ai_questions_success_ollama()
    # test_generate_ai_questions_success_openai()
    # ... and so on for all tests ...
    # test_get_llm_provider_defaults_to_ollama()
    # ...
    # test_category_filtering()
    
    print("\nNote: For full test discovery and reporting, run with `pytest` command.")
    print("\n🎉 AI integration and provider tests setup complete!")
    # To actually run them if script is executed directly:
    pytest.main([__file__]) # Runs pytest on this file