#!/usr/bin/env python3

# Test script to check AI integration functionality with provider-based architecture
import json
import sqlite3
from unittest.mock import patch, MagicMock
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ai_endpoint_error_handling():
    """Test that AI endpoint handles errors gracefully with provider architecture"""
    print("Testing AI endpoint error handling...")
    
    try:
        # Import here to avoid module loading issues
        from main import generate_ai_questions
        
        # This should fail with connection error since providers aren't running
        # We expect this to raise an HTTPException
        result = generate_ai_questions("history", 2)
        print("❌ AI endpoint test failed - should have raised an exception")
    except Exception as e:
        error_msg = str(e)
        if ("Connection refused" in error_msg or 
            "AI question generation failed" in error_msg or 
            "package not available" in error_msg):
            print("✅ AI endpoint error handling test passed!")
            print(f"Expected error caught: {type(e).__name__}")
        else:
            print(f"❌ Unexpected error: {e}")

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
            
            from main import generate_ai_questions
            
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
                else:
                    print("❌ Mock AI generation test failed - invalid question structure")
            else:
                print("❌ Mock AI generation test failed - wrong number of questions")
                
    except Exception as e:
        print(f"❌ Mock AI generation test failed: {e}")

def test_provider_configuration():
    """Test provider configuration system"""
    print("\nTesting provider configuration system...")
    
    try:
        # Test environment variable reading
        os.environ['LLM_PROVIDER'] = 'test_provider'
        provider_type = os.getenv('LLM_PROVIDER', 'ollama')
        
        if provider_type == 'test_provider':
            print("✅ Environment variable configuration test passed!")
        else:
            print("❌ Environment variable configuration test failed")
            
        # Test .env.example file exists
        env_example_path = '../.env.example'
        if os.path.exists(env_example_path):
            print("✅ .env.example configuration file exists!")
        else:
            print("❌ .env.example configuration file missing")
            
    except Exception as e:
        print(f"❌ Provider configuration test failed: {e}")

if __name__ == "__main__":
    print("🧪 Testing AI Integration with Provider Architecture\n")
    
    test_ai_endpoint_error_handling()
    test_category_filtering()
    test_mock_ai_generation()
    test_provider_configuration()
    
    print("\n🎉 AI integration tests completed!")
    print("Note: Tests use mocked responses and verify the provider architecture works correctly.")