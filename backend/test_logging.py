#!/usr/bin/env python3

"""
Test script for the logging system
"""

import sys
import os
import tempfile
import shutil

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_logger():
    """Test the logging system functionality"""
    print("Testing logging system...")
    
    from logger import info, debug, warning, error, get_logs, set_log_level
    
    # Test logging functions
    info("Test info message from logger test", "test")
    debug("Test debug message from logger test", "test")
    warning("Test warning message from logger test", "test") 
    error("Test error message from logger test", "test")
    
    # Test log retrieval
    logs = get_logs(limit=10)
    print(f"Retrieved {len(logs['logs'])} log entries")
    
    # Verify we have logs
    assert len(logs['logs']) > 0, "No logs retrieved"
    
    # Test filtering by level
    error_logs = get_logs(level="ERROR", limit=5)
    print(f"Retrieved {len(error_logs['logs'])} error logs")
    
    # Test filtering by module
    test_logs = get_logs(module="test", limit=10)
    print(f"Retrieved {len(test_logs['logs'])} test module logs")
    
    # Test log level change
    set_log_level("DEBUG")
    debug("This debug message should appear after level change", "test")
    
    print("✅ Logging system test passed!")
    
    return True

def test_log_structure():
    """Test the structure of log entries"""
    print("Testing log entry structure...")
    
    from logger import get_logs
    
    logs = get_logs(limit=1)
    if logs['logs']:
        log_entry = logs['logs'][0]
        required_fields = ['id', 'timestamp', 'level', 'module', 'message', 'created_at']
        
        for field in required_fields:
            assert field in log_entry, f"Missing field: {field}"
        
        # Verify log levels are valid
        assert log_entry['level'] in ['DEBUG', 'INFO', 'WARNING', 'ERROR'], f"Invalid log level: {log_entry['level']}"
        
        print(f"Sample log entry: {log_entry}")
        print("✅ Log structure test passed!")
    else:
        print("⚠️  No logs available for structure test")
    
    return True

if __name__ == "__main__":
    try:
        test_logger()
        test_log_structure()
        print("\n🎉 All logging tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)