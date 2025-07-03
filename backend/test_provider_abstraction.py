#!/usr/bin/env python3

# Basic test script to check the provider abstraction
import json
import os
import sys
from unittest.mock import patch, MagicMock

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test the provider abstraction without FastAPI dependencies
def test_provider_abstraction():
    """Test provider abstraction without dependencies"""
    print("Testing provider abstraction...")
    
    try:
        # Test importing the provider module
        from llm_providers import create_llm_provider, OllamaProvider, OpenAIProvider
        print("✅ Successfully imported llm_providers module")
        
        # Test provider factory with ollama
        os.environ['LLM_PROVIDER'] = 'ollama'
        provider = create_llm_provider()
        if isinstance(provider, OllamaProvider):
            print("✅ Ollama provider creation test passed")
        else:
            print("❌ Ollama provider creation test failed")
        
        # Test provider factory with openai
        os.environ['LLM_PROVIDER'] = 'openai'
        os.environ['OPENAI_API_KEY'] = 'test-key'
        provider = create_llm_provider()
        if isinstance(provider, OpenAIProvider):
            print("✅ OpenAI provider creation test passed")
        else:
            print("❌ OpenAI provider creation test failed")
            
    except Exception as e:
        print(f"❌ Provider abstraction test failed: {e}")

def test_environment_config():
    """Test environment configuration"""
    print("\nTesting environment configuration...")
    
    try:
        # Test .env.example file exists
        if os.path.exists("../.env.example"):
            print("✅ .env.example file exists")
        else:
            print("❌ .env.example file missing")
            
        # Test environment variable reading
        os.environ['LLM_PROVIDER'] = 'test_provider'
        provider_type = os.getenv('LLM_PROVIDER', 'ollama')
        if provider_type == 'test_provider':
            print("✅ Environment variable reading test passed")
        else:
            print("❌ Environment variable reading test failed")
            
    except Exception as e:
        print(f"❌ Environment configuration test failed: {e}")

def test_mock_providers():
    """Test providers with mocked dependencies"""
    print("\nTesting providers with mocked dependencies...")
    
    try:
        # Mock ollama module import
        with patch.dict('sys.modules', {'ollama': MagicMock()}):
            import sys
            sys.modules['ollama'].chat = MagicMock(return_value={
                'message': {
                    'content': '[{"text": "Test?", "options": [{"id": "a", "text": "A"}], "correct_answer": "a"}]'
                }
            })
            
            from llm_providers import OllamaProvider
            provider = OllamaProvider()
            result = provider.generate_questions("test", 1)
            
            if result and len(result) == 1:
                print("✅ Ollama provider mock test passed")
            else:
                print("❌ Ollama provider mock test failed")
                
        # Mock OpenAI module import
        with patch.dict('sys.modules', {'openai': MagicMock()}):
            import sys
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = '[{"text": "Test?", "options": [{"id": "a", "text": "A"}], "correct_answer": "a"}]'
            mock_client.chat.completions.create.return_value = mock_response
            sys.modules['openai'].OpenAI = MagicMock(return_value=mock_client)
            
            from llm_providers import OpenAIProvider
            provider = OpenAIProvider(api_key="test-key")
            result = provider.generate_questions("test", 1)
            
            if result and len(result) == 1:
                print("✅ OpenAI provider mock test passed")
            else:
                print("❌ OpenAI provider mock test failed")
                
    except Exception as e:
        print(f"❌ Mock providers test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Testing Provider Abstraction\n")
    
    test_provider_abstraction()
    test_environment_config()
    test_mock_providers()
    
    print("\n🎉 Provider abstraction tests completed!")