#!/usr/bin/env python3

"""Simple AI integration test that doesn't make actual API calls"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ai_providers_import():
    """Test that AI providers can be imported"""
    print("Testing AI providers import...")
    
    try:
        from llm_providers import get_available_providers, get_available_models
        print("✅ AI providers import test passed!")
        return True
    except Exception as e:
        print(f"❌ AI providers import test failed: {e}")
        return False

def test_configuration_loading():
    """Test that configuration can be loaded"""
    print("Testing configuration loading...")
    
    try:
        from config_manager import config_manager
        config = config_manager.get_config()
        
        if config and 'llm_provider' in config:
            print("✅ Configuration loading test passed!")
            print(f"Current provider: {config['llm_provider']}")
            return True
        else:
            print("❌ Configuration loading test failed - missing provider config")
            return False
    except Exception as e:
        print(f"❌ Configuration loading test failed: {e}")
        return False

def test_database_connection():
    """Test database connection works"""
    print("Testing database connection...")
    
    try:
        import sqlite3
        conn = sqlite3.connect('quiz.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM questions")
        count = cursor.fetchone()[0]
        conn.close()
        
        print(f"✅ Database connection test passed! Found {count} questions")
        return True
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def test_fastapi_import():
    """Test FastAPI app can be imported"""
    print("Testing FastAPI app import...")
    
    try:
        from main import app
        print("✅ FastAPI app import test passed!")
        return True
    except Exception as e:
        print(f"❌ FastAPI app import test failed: {e}")
        return False

def test_environment_variables():
    """Test environment variable handling"""
    print("Testing environment variables...")
    
    try:
        # Test setting and getting environment variables
        os.environ['TEST_VAR'] = 'test_value'
        value = os.getenv('TEST_VAR')
        
        if value == 'test_value':
            print("✅ Environment variables test passed!")
            return True
        else:
            print("❌ Environment variables test failed")
            return False
    except Exception as e:
        print(f"❌ Environment variables test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing AI Integration Components\n")
    
    # Run tests
    tests = [
        test_ai_providers_import,
        test_configuration_loading,
        test_database_connection,
        test_fastapi_import,
        test_environment_variables
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Empty line for readability
    
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All AI integration component tests passed!")
        sys.exit(0)
    else:
        print("⚠️ Some tests failed")
        sys.exit(1)
