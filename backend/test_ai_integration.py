#!/usr/bin/env python3

# Test script to check AI integration functionality
import json
import sqlite3
from unittest.mock import patch, MagicMock
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import generate_ai_questions

def test_ai_endpoint_error_handling():
    """Test that AI endpoint handles errors gracefully"""
    print("Testing AI endpoint error handling...")
    
    try:
        # This should fail with connection error since Ollama isn't running
        # We expect this to raise an HTTPException
        result = generate_ai_questions("history", 2)
        print("❌ AI endpoint test failed - should have raised an exception")
    except Exception as e:
        if "Connection refused" in str(e) or "AI question generation failed" in str(e):
            print("✅ AI endpoint error handling test passed!")
            print(f"Expected error caught: {type(e).__name__}")
        else:
            print(f"❌ Unexpected error: {e}")

def test_category_filtering():
    """Test that category filtering works with database questions"""
    print("\nTesting category filtering...")
    
    # Import the get_questions function
    from main import get_questions
    
    try:
        # Test getting geography questions
        geography_questions = get_questions(category="geography", limit=2)
        
        if geography_questions and len(geography_questions) > 0:
            # Check that all returned questions are geography
            all_geography = all(q.get("category") == "geography" for q in geography_questions)
            if all_geography:
                print("✅ Category filtering test passed!")
                print(f"Retrieved {len(geography_questions)} geography questions")
            else:
                print("❌ Category filtering test failed - not all questions are geography")
        else:
            print("❌ Category filtering test failed - no questions returned")
    except Exception as e:
        print(f"❌ Category filtering test failed: {e}")

def test_mock_ai_generation():
    """Test AI generation with mocked Ollama response"""
    print("\nTesting AI generation with mock...")
    
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
    
    with patch('main.ollama.chat', return_value=mock_response):
        try:
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

if __name__ == "__main__":
    print("🧪 Testing AI Integration Features\n")
    
    test_ai_endpoint_error_handling()
    test_category_filtering()
    test_mock_ai_generation()
    
    print("\n🎉 AI integration tests completed!")