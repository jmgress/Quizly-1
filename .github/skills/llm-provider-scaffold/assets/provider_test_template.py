"""Test template for a new Quizly LLM provider.

Replace placeholders:
  <name>  -> lowercase provider id, e.g. "anthropic"
  <Name>  -> PascalCase class prefix, e.g. "Anthropic"
  <NAME>  -> UPPERCASE env prefix, e.g. "ANTHROPIC"

Place at: tests/backend/unit/test_<name>_provider.py
No real network calls — the external client is always mocked.
"""

import pytest
from unittest.mock import patch, MagicMock

from llm_providers.<name>_provider import <Name>Provider


class Test<Name>ProviderInit:
    def test_raises_when_api_key_missing(self, monkeypatch):
        # Arrange
        monkeypatch.delenv("<NAME>_API_KEY", raising=False)
        # Act / Assert
        with pytest.raises(ValueError):
            <Name>Provider(api_key=None)

    def test_initializes_with_api_key(self):
        # Arrange / Act
        provider = <Name>Provider(api_key="test-key", model="test-model")
        # Assert
        assert provider.api_key == "test-key"
        assert provider.model == "test-model"


class Test<Name>ProviderGenerate:
    @patch("llm_providers.<name>_provider.<Name>Provider._parse_response")
    def test_generate_questions_returns_parsed_result(self, mock_parse):
        # Arrange
        provider = <Name>Provider(api_key="test-key")
        provider._client = MagicMock()
        expected = [{"text": "Q1", "options": ["a", "b"], "correct_answer": "a"}]
        mock_parse.return_value = expected
        # Act
        result = provider.generate_questions("math", limit=1)
        # Assert
        assert result == expected

    def test_generate_questions_raises_without_client(self):
        # Arrange
        provider = <Name>Provider(api_key="test-key")
        provider._client = None
        # Act / Assert
        with pytest.raises(RuntimeError):
            provider.generate_questions("math", limit=1)


class Test<Name>ProviderHealthCheck:
    def test_health_check_false_without_client(self):
        # Arrange
        provider = <Name>Provider(api_key="test-key")
        provider._client = None
        # Act / Assert
        assert provider.health_check() is False

    def test_health_check_true_with_client(self):
        # Arrange
        provider = <Name>Provider(api_key="test-key")
        provider._client = MagicMock()
        # Act / Assert
        assert provider.health_check() is True
