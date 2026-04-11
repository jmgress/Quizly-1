"""Tests for OpenAI API connectivity.

These tests are skipped when OPENAI_API_KEY is not set in the environment.
"""

import os
import sys
import pytest
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

load_dotenv()

pytestmark = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set",
)


def test_openai_api_connection():
    """Test that the OpenAI API responds with the configured model."""
    import openai

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Hello, please respond with a simple greeting."}],
        max_tokens=20,
        timeout=10,
    )

    assert response.choices, "Expected at least one choice in the response"
    content = response.choices[0].message.content
    assert isinstance(content, str) and len(content) > 0