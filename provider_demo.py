#!/usr/bin/env python3
"""
Quick demonstration of the new provider-based LLM integration.
Shows how to use the system with different providers.
"""

import os
import sys
from unittest.mock import patch, MagicMock

# Add backend to path
sys.path.insert(0, '/home/runner/work/Quizly-1/Quizly-1/backend')

def demo_provider_switching():
    """Demonstrate switching between providers"""
    print("🔄 Provider Switching Demo")
    print("=" * 40)
    
    # Mock the external dependencies
    with patch.dict('sys.modules', {
        'ollama': MagicMock(),
        'openai': MagicMock()
    }):
        # Set up mocks
        import sys
        sys.modules['ollama'].chat = MagicMock(return_value={
            'message': {'content': '[{"text": "Ollama question", "options": [{"id": "a", "text": "A"}], "correct_answer": "a"}]'}
        })
        
        mock_openai_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '[{"text": "OpenAI question", "options": [{"id": "a", "text": "A"}], "correct_answer": "a"}]'
        mock_openai_client.chat.completions.create.return_value = mock_response
        sys.modules['openai'].OpenAI = MagicMock(return_value=mock_openai_client)
        
        from llm_providers import create_llm_provider
        
        # Demo 1: Ollama provider
        print("\n1. Using Ollama Provider:")
        os.environ['LLM_PROVIDER'] = 'ollama'
        provider = create_llm_provider()
        result = provider.generate_questions("demo", 1)
        print(f"   Provider: {type(provider).__name__}")
        print(f"   Generated: {result[0]['text']}")
        
        # Demo 2: OpenAI provider
        print("\n2. Using OpenAI Provider:")
        os.environ['LLM_PROVIDER'] = 'openai'
        os.environ['OPENAI_API_KEY'] = 'demo-key'
        provider = create_llm_provider()
        result = provider.generate_questions("demo", 1)
        print(f"   Provider: {type(provider).__name__}")
        print(f"   Generated: {result[0]['text']}")
        
        # Demo 3: Custom configuration
        print("\n3. Custom Configuration:")
        provider = create_llm_provider('ollama', model='custom-model')
        print(f"   Provider: {type(provider).__name__}")
        print(f"   Model: {provider.model}")

def demo_configuration():
    """Demonstrate configuration options"""
    print("\n⚙️  Configuration Demo")
    print("=" * 40)
    
    print("\n1. Environment Variables:")
    print(f"   LLM_PROVIDER: {os.getenv('LLM_PROVIDER', 'ollama')}")
    print(f"   OLLAMA_MODEL: {os.getenv('OLLAMA_MODEL', 'llama3.2')}")
    print(f"   OPENAI_MODEL: {os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')}")
    
    print("\n2. Configuration File:")
    if os.path.exists('.env.example'):
        print("   ✅ .env.example found")
        with open('.env.example', 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
            print(f"   📋 Contains {len(lines)} configuration options")
    else:
        print("   ❌ .env.example not found")

if __name__ == "__main__":
    print("🎯 Quizly Provider-Based LLM Integration Demo")
    print("=" * 50)
    
    demo_provider_switching()
    demo_configuration()
    
    print("\n🎉 Demo Complete!")
    print("\nKey Benefits:")
    print("✅ Easy switching between LLM providers")
    print("✅ Environment-based configuration")
    print("✅ No code changes needed to switch providers")
    print("✅ Backwards compatibility maintained")
    print("✅ Extensible architecture for future providers")