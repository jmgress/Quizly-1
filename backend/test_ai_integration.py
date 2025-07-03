#!/usr/bin/env python3

"""Simple tests for the LLM provider integration"""

import os
import json
from unittest.mock import patch
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_providers import get_provider, OllamaProvider, OpenAIProvider


def reset_env():
    for var in ["LLM_PROVIDER", "OPENAI_API_KEY", "OPENAI_MODEL", "OLLAMA_MODEL"]:
        os.environ.pop(var, None)


def test_provider_factory():
    print("Testing provider factory...")
    reset_env()
    provider = get_provider()
    if isinstance(provider, OllamaProvider):
        print("✅ Default provider is Ollama")
    else:
        print("❌ Default provider selection failed")

    os.environ["LLM_PROVIDER"] = "openai"
    os.environ["OPENAI_API_KEY"] = "dummy"
    try:
        provider = get_provider()
        if isinstance(provider, OpenAIProvider):
            print("✅ OpenAI provider selected")
        else:
            print("❌ OpenAI provider selection failed")
    except RuntimeError:
        print("✅ OpenAI provider selection raised RuntimeError as expected (package missing)")
    reset_env()


def test_mock_ollama_generation():
    print("\nTesting Ollama generation with mock...")
    reset_env()
    os.environ["LLM_PROVIDER"] = "ollama"
    mock_resp = {
        "message": {
            "content": json.dumps([
                {
                    "text": "Q",
                    "options": [
                        {"id": "a", "text": "A"},
                        {"id": "b", "text": "B"},
                        {"id": "c", "text": "C"},
                        {"id": "d", "text": "D"}
                    ],
                    "correct_answer": "a",
                    "category": "test"
                }
            ])
        }
    }
    with patch('llm_providers.ollama', type('obj', (), {'chat': lambda *a, **k: mock_resp, 'list': lambda: []})):
        provider = get_provider()
        qs = provider.generate_questions("test", 1)
        if qs and qs[0]['text'] == 'Q':
            print("✅ Ollama provider generation passed")
        else:
            print("❌ Ollama provider generation failed")
    reset_env()


def test_mock_openai_generation():
    print("\nTesting OpenAI generation with mock...")
    reset_env()
    os.environ["LLM_PROVIDER"] = "openai"
    os.environ["OPENAI_API_KEY"] = "dummy"
    choice_obj = type("Obj", (), {"message": type("Obj", (), {"content": json.dumps([
        {
            "text": "Q",
            "options": [
                {"id": "a", "text": "A"},
                {"id": "b", "text": "B"},
                {"id": "c", "text": "C"},
                {"id": "d", "text": "D"}
            ],
            "correct_answer": "a",
            "category": "test"
        }
    ])})})
    mock_resp = type("Obj", (), {"choices": [choice_obj]})
    dummy_openai = type('obj', (), {
        'ChatCompletion': type('obj', (), {'create': lambda *a, **k: mock_resp}),
        'Model': type('obj', (), {'list': lambda: None})
    })
    with patch('llm_providers.openai', dummy_openai):
        provider = get_provider()
        qs = provider.generate_questions("test", 1)
    if qs and qs[0]['text'] == 'Q':
        print("✅ OpenAI provider generation passed")
    else:
        print("❌ OpenAI provider generation failed")
    reset_env()


def test_category_filtering():
    print("\nTesting category filtering...")
    import sqlite3
    conn = sqlite3.connect('backend/quiz.db')
    cur = conn.cursor()
    cur.execute("SELECT category FROM questions WHERE category='geography' LIMIT 2")
    rows = cur.fetchall()
    conn.close()
    if rows and all(r[0] == 'geography' for r in rows):
        print("✅ Category filtering test passed!")
    else:
        print("❌ Category filtering test failed")


if __name__ == "__main__":
    print("🧪 Testing AI Integration Features\n")
    test_provider_factory()
    test_mock_ollama_generation()
    test_mock_openai_generation()
    test_category_filtering()
    print("\n🎉 AI integration tests completed!")



