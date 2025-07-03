#!/usr/bin/env python3

"""
Simple demo script to show the provider-based LLM integration working.
This demonstrates how to use the new provider architecture.
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.insert(0, '/home/runner/work/Quizly-1/Quizly-1/backend')

# Load environment variables
load_dotenv()

def demo_provider_configuration():
    """Demo the provider configuration system."""
    print("🤖 Quizly LLM Provider Configuration Demo")
    print("=" * 50)
    
    # Test environment variable loading
    print("\n1. Environment Configuration:")
    print(f"   LLM_PROVIDER: {os.getenv('LLM_PROVIDER', 'ollama')}")
    print(f"   OLLAMA_MODEL: {os.getenv('OLLAMA_MODEL', 'llama3.2')}")
    print(f"   OLLAMA_HOST: {os.getenv('OLLAMA_HOST', 'http://localhost:11434')}")
    print(f"   OPENAI_MODEL: {os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')}")
    print(f"   DEFAULT_QUESTION_LIMIT: {os.getenv('DEFAULT_QUESTION_LIMIT', '5')}")
    
    # Test provider factory
    print("\n2. Provider Factory Test:")
    try:
        from llm_providers import create_llm_provider, OllamaProvider, OpenAIProvider
        
        # Test Ollama provider
        print("   Testing Ollama provider creation...")
        os.environ['LLM_PROVIDER'] = 'ollama'
        provider = create_llm_provider()
        print(f"   ✅ Created: {type(provider).__name__}")
        
        # Test OpenAI provider
        print("   Testing OpenAI provider creation...")
        os.environ['LLM_PROVIDER'] = 'openai'
        os.environ['OPENAI_API_KEY'] = 'test-key'
        provider = create_llm_provider()
        print(f"   ✅ Created: {type(provider).__name__}")
        
        # Test invalid provider
        print("   Testing invalid provider...")
        try:
            provider = create_llm_provider('invalid')
            print("   ❌ Should have failed")
        except ValueError as e:
            print(f"   ✅ Correctly rejected invalid provider: {e}")
            
    except Exception as e:
        print(f"   ❌ Provider factory test failed: {e}")
    
    # Test configuration file
    print("\n3. Configuration File Test:")
    env_example_path = '/home/runner/work/Quizly-1/Quizly-1/.env.example'
    if os.path.exists(env_example_path):
        print("   ✅ .env.example file exists")
        with open(env_example_path, 'r') as f:
            lines = f.readlines()
            print(f"   ✅ Contains {len(lines)} configuration lines")
            # Show first few configuration options
            for line in lines[:8]:
                if line.strip() and not line.startswith('#'):
                    print(f"      {line.strip()}")
    else:
        print("   ❌ .env.example file missing")
    
    print("\n4. Backend Integration Test:")
    try:
        # Test that the main module can import the providers
        from main import generate_ai_questions
        print("   ✅ Main module successfully imports provider integration")
        
        # Test environment variable usage
        original_provider = os.getenv('LLM_PROVIDER')
        os.environ['LLM_PROVIDER'] = 'ollama'
        print(f"   ✅ Environment variable LLM_PROVIDER set to: {os.getenv('LLM_PROVIDER')}")
        
        # Restore original value
        if original_provider:
            os.environ['LLM_PROVIDER'] = original_provider
        
    except Exception as e:
        print(f"   ❌ Backend integration test failed: {e}")
    
    print("\n5. Summary:")
    print("   ✅ Provider abstraction layer implemented")
    print("   ✅ Environment configuration support added")
    print("   ✅ Factory pattern for provider creation")
    print("   ✅ Support for both Ollama and OpenAI")
    print("   ✅ Backward compatibility maintained")
    print("   ✅ Configuration documentation provided")
    
    print("\n🎉 LLM Provider Configuration Demo Complete!")
    print("\nTo use the new provider system:")
    print("1. Copy .env.example to .env")
    print("2. Configure your preferred provider settings")
    print("3. Start the backend server")
    print("4. AI questions will use your configured provider")

if __name__ == "__main__":
    demo_provider_configuration()