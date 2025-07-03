#!/usr/bin/env python3

# Test script to check AI integration functionality with multiple providers
import json
import sqlite3
from unittest.mock import patch, MagicMock
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import generate_ai_questions
from llm_providers import create_llm_provider, OllamaProvider, OpenAIProvider

def test_ai_endpoint_error_handling():
    """Test that AI endpoint handles errors gracefully"""
    print("Testing AI endpoint error handling...")
    
    try:
        # This should fail with connection error since providers aren't running
        # We expect this to raise an HTTPException
        result = generate_ai_questions("history", 2)
        print("❌ AI endpoint test failed - should have raised an exception")
    except Exception as e:
        if "Connection refused" in str(e) or "AI question generation failed" in str(e):
            print("✅ AI endpoint error handling test passed!")
            print(f"Expected error caught: {type(e).__name__}")
        else:
            print(f"❌ Unexpected error: {e}")


def test_ollama_provider():
    """Test Ollama provider with mocked response"""
    print("\nTesting Ollama provider with mock...")
    
    # Mock the ollama.chat function
    mock_response = {
        'message': {
            'content': '''[
                {
                    "text": "What year did World War II end?",
                    "options": [
                        {"id": "a", "text": "1943"},
                        {"id": "b", "text": "1945"},
                        {"id": "c", "text": "1947"},
                        {"id": "d", "text": "1949"}
                    ],
                    "correct_answer": "b",
                    "category": "history"
                }
            ]'''
        }
    }
    
    with patch('llm_providers.ollama.chat', return_value=mock_response):
        try:
            os.environ['LLM_PROVIDER'] = 'ollama'
            provider = create_llm_provider()
            result = provider.generate_questions("history", 1)
            
            if result and len(result) == 1:
                question = result[0]
                if (question.get('text') and 
                    question.get('options') and 
                    question.get('correct_answer') and
                    question.get('id') >= 1000):
                    print("✅ Ollama provider test passed!")
                    print(f"Generated question: {question['text']}")
                else:
                    print("❌ Ollama provider test failed - invalid question structure")
            else:
                print("❌ Ollama provider test failed - wrong number of questions")
        except Exception as e:
            print(f"❌ Ollama provider test failed: {e}")


def test_openai_provider():
    """Test OpenAI provider with mocked response"""
    print("\nTesting OpenAI provider with mock...")
    
    # Mock the OpenAI client
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '''[
        {
            "text": "What is the capital of France?",
            "options": [
                {"id": "a", "text": "London"},
                {"id": "b", "text": "Berlin"},
                {"id": "c", "text": "Paris"},
                {"id": "d", "text": "Madrid"}
            ],
            "correct_answer": "c",
            "category": "geography"
        }
    ]'''
    
    with patch('llm_providers.openai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        try:
            os.environ['LLM_PROVIDER'] = 'openai'
            os.environ['OPENAI_API_KEY'] = 'test-key'
            provider = create_llm_provider()
            result = provider.generate_questions("geography", 1)
            
            if result and len(result) == 1:
                question = result[0]
                if (question.get('text') and 
                    question.get('options') and 
                    question.get('correct_answer') and
                    question.get('id') >= 1000):
                    print("✅ OpenAI provider test passed!")
                    print(f"Generated question: {question['text']}")
                else:
                    print("❌ OpenAI provider test failed - invalid question structure")
            else:
                print("❌ OpenAI provider test failed - wrong number of questions")
        except Exception as e:
            print(f"❌ OpenAI provider test failed: {e}")


def test_provider_factory():
    """Test provider factory function"""
    print("\nTesting provider factory...")
    
    try:
        # Test Ollama provider creation
        os.environ['LLM_PROVIDER'] = 'ollama'
        provider = create_llm_provider()
        if isinstance(provider, OllamaProvider):
            print("✅ Ollama provider factory test passed!")
        else:
            print("❌ Ollama provider factory test failed - wrong type")
        
        # Test OpenAI provider creation
        os.environ['LLM_PROVIDER'] = 'openai'
        os.environ['OPENAI_API_KEY'] = 'test-key'
        provider = create_llm_provider()
        if isinstance(provider, OpenAIProvider):
            print("✅ OpenAI provider factory test passed!")
        else:
            print("❌ OpenAI provider factory test failed - wrong type")
            
    except Exception as e:
        print(f"❌ Provider factory test failed: {e}")


def test_configuration_validation():
    """Test configuration validation"""
    print("\nTesting configuration validation...")
    
    try:
        # Test missing OpenAI API key
        os.environ['LLM_PROVIDER'] = 'openai'
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        try:
            provider = create_llm_provider()
            print("❌ Configuration validation test failed - should have raised error for missing API key")
        except ValueError as e:
            if "API key" in str(e):
                print("✅ Configuration validation test passed!")
            else:
                print(f"❌ Configuration validation test failed - wrong error: {e}")
        
        # Test invalid provider type
        try:
            provider = create_llm_provider("invalid_provider")
            print("❌ Configuration validation test failed - should have raised error for invalid provider")
        except ValueError as e:
            if "Unknown provider" in str(e):
                print("✅ Invalid provider validation test passed!")
            else:
                print(f"❌ Invalid provider validation test failed - wrong error: {e}")
                
    except Exception as e:
        print(f"❌ Configuration validation test failed: {e}")


def test_category_filtering():
    """Test that category filtering works with database questions"""
    print("\nTesting category filtering...")
    
    try:
        # Connect to database
        conn = sqlite3.connect('quiz.db')
        cursor = conn.cursor()
        
        # Get geography questions
        cursor.execute("SELECT * FROM questions WHERE category = 'geography'")
        geo_questions = cursor.fetchall()
        
        if geo_questions:
            print("✅ Category filtering test passed!")
            print(f"Found {len(geo_questions)} geography questions")
        else:
            print("❌ Category filtering test failed - no geography questions found")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Category filtering test failed: {e}")


if __name__ == "__main__":
    print("🧪 Testing AI Integration with Multiple Providers\n")
    
    test_ai_endpoint_error_handling()
    test_ollama_provider()
    test_openai_provider()
    test_provider_factory()
    test_configuration_validation()
    test_category_filtering()
    
    print("\n🎉 AI integration tests completed!")
    print("Note: Some tests use mocked responses and may not reflect actual provider behavior.")