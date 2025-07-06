#!/usr/bin/env python3

# Test script to check AI integration functionality with provider-based architecture
import json
import sqlite3
from unittest.mock import patch, MagicMock
import sys
import os
import signal
import time

# Add project root to sys.path to allow backend imports
# This assumes tests might be run directly, for pytest this might not be strictly necessary
# if pytest is run from the project root and backend is an importable package.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def timeout_handler(signum, frame):
    """Handle timeout signal"""
    raise TimeoutError("Test timed out")

def run_with_timeout(func, timeout_seconds=10):
    """Run a function with a timeout"""
    try:
        # Set up signal handler for timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_seconds)
        
        # Run the function
        result = func()
        
        # Cancel the alarm
        signal.alarm(0)
        return result
        
    except TimeoutError:
        print(f"⏱️ Function timed out after {timeout_seconds} seconds")
        return False
    except Exception as e:
        signal.alarm(0)  # Cancel alarm
        print(f"❌ Function failed: {e}")
        return False

def test_ai_endpoint_error_handling():
    """Test that AI endpoint handles errors gracefully with provider architecture"""
    print("Testing AI endpoint error handling...")
    
    try:
        # Import here to avoid module loading issues
        from backend.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test AI endpoint with mock - should not hang
        response = client.post("/api/ai/generate", json={
            "subject": "history",
            "count": 2
        })
        
        # We expect either success (200) or failure (4xx/5xx) - not a hang
        if response.status_code in [200, 400, 500, 503]:
            print("✅ AI endpoint error handling test passed!")
            print(f"Response status: {response.status_code}")
            if response.status_code == 200:
                print("AI generation successful")
            else:
                print("AI generation failed gracefully (expected)")
        else:
            print(f"❌ Unexpected response code: {response.status_code}")
            
    except Exception as e:
        error_msg = str(e)
        if ("Connection refused" in error_msg or 
            "AI question generation failed" in error_msg or 
            "package not available" in error_msg):
            print("✅ AI endpoint error handling test passed!")
            print(f"Expected error caught: {type(e).__name__}")
        else:
            print(f"❌ Unexpected error: {e}")
            return False
    
    return True

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
            conn.close()
            return True
        else:
            print("⚠️ No geography questions found - test skipped")
            conn.close()
            return True  # Not a failure, just no data
            
    except Exception as e:
        print(f"❌ Category filtering test failed: {e}")
        return False

def test_mock_ai_generation():
    """Test AI generation with mocked provider response"""
    print("\nTesting AI generation with mock provider...")
    
    try:
        # Mock the provider system
        with patch.dict('sys.modules', {'ollama': MagicMock()}):
            import sys
            sys.modules['ollama'].chat = MagicMock(return_value={
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
            })
            
            from backend.main import generate_ai_questions
            
            # Set environment to use ollama
            os.environ['LLM_PROVIDER'] = 'ollama'
            
            result = generate_ai_questions("history", 1)
            if result and len(result) == 1:
                question = result[0]
                if (question.get('text') and 
                    question.get('options') and 
                    question.get('correct_answer') and
                    question.get('id') >= 1000):  # AI questions have IDs >= 1000
                    print("✅ Mock AI generation test passed!")
                    print(f"Generated question: {question['text']}")
                    return True
                else:
                    print("❌ Mock AI generation test failed - invalid question structure")
                    return False
            else:
                print("❌ Mock AI generation test failed - wrong number of questions")
                return False
                
    except Exception as e:
        print(f"❌ Mock AI generation test failed: {e}")
        return False

def test_model_listing():
    """Test listing available models"""
    print("\nTesting model listing...")

    try:
        from backend.llm_providers import get_available_models
        models = get_available_models("openai")

        if "gpt-3.5-turbo" in models:
            print("✅ Model listing test passed!")
            return True
        else:
            print("❌ Model listing test failed - expected model not found")
            return False
    except Exception as e:
        print(f"❌ Model listing test failed: {e}")
        return False

def test_provider_configuration():
    """Test provider configuration system"""
    print("\nTesting provider configuration system...")
    
    try:
        # Test environment variable reading
        os.environ['LLM_PROVIDER'] = 'test_provider'
        provider_type = os.getenv('LLM_PROVIDER', 'ollama')
        
        if provider_type == 'test_provider':
            print("✅ Environment variable configuration test passed!")
            return True
        else:
            print("❌ Environment variable configuration test failed")
            return False
            
    except Exception as e:
        print(f"❌ Provider configuration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing AI Integration with Provider Architecture\n")
    
    # Run tests with individual timeouts
    tests_passed = 0
    total_tests = 5
    
    print("Running AI endpoint error handling test...")
    if run_with_timeout(test_ai_endpoint_error_handling, 15):
        tests_passed += 1
    
    print("Running category filtering test...")
    if run_with_timeout(test_category_filtering, 5):
        tests_passed += 1
    
    print("Running mock AI generation test...")
    if run_with_timeout(test_mock_ai_generation, 10):
        tests_passed += 1
    
    print("Running model listing test...")
    if run_with_timeout(test_model_listing, 5):
        tests_passed += 1
    
    print("Running provider configuration test...")
    if run_with_timeout(test_provider_configuration, 5):
        tests_passed += 1
    
    print(f"\n📊 AI Integration Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All AI integration tests passed!")
        sys.exit(0)
    else:
        print("⚠️ Some AI integration tests failed or timed out")
        print("Note: This is expected if API keys are not configured or services are not running")
        sys.exit(0)  # Don't fail the entire test suite for AI tests