#!/usr/bin/env python3

"""
Test script to verify the new database module functionality.
"""

import os
import sqlite3
import tempfile
import logging

# Set up logging to see the status messages
logging.basicConfig(level=logging.INFO)

def test_database_module():
    """Test the separated database module functionality"""
    print("Testing separated database module...")
    
    # Test in a temporary directory to avoid affecting the main database
    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to temp directory
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Import and test the database module
            import sys
            sys.path.insert(0, original_dir)
            from database import init_db
            
            # Test 1: Initialize database when file doesn't exist
            print("\n1. Testing initial database creation...")
            init_db()
            
            # Verify database was created with correct structure
            conn = sqlite3.connect('quiz.db')
            cursor = conn.cursor()
            
            # Check questions table exists and has correct data
            cursor.execute("SELECT COUNT(*) FROM questions")
            question_count = cursor.fetchone()[0]
            print(f"   Total questions: {question_count}")
            
            # Check category distribution
            cursor.execute("SELECT category, COUNT(*) FROM questions GROUP BY category ORDER BY category")
            category_counts = cursor.fetchall()
            print("   Questions per category:")
            for cat, count in category_counts:
                print(f"     {cat}: {count}")
            
            # Test 2: Verify conditional initialization (should skip)
            print("\n2. Testing conditional initialization...")
            init_db()  # Should skip since database exists
            
            # Verify count hasn't changed
            cursor.execute("SELECT COUNT(*) FROM questions")
            new_count = cursor.fetchone()[0]
            print(f"   Questions after second init: {new_count}")
            
            conn.close()
            
            # Validate results
            if question_count == 25:
                print("✅ Database creation test passed!")
            else:
                print(f"❌ Database creation test failed - expected 25 questions, got {question_count}")
                
            if len(category_counts) == 5 and all(count == 5 for _, count in category_counts):
                print("✅ Category distribution test passed!")
            else:
                print("❌ Category distribution test failed")
                
            if new_count == question_count:
                print("✅ Conditional initialization test passed!")
            else:
                print("❌ Conditional initialization test failed")
                
        finally:
            os.chdir(original_dir)

def test_main_integration():
    """Test that main.py properly integrates with the database module"""
    print("\n\nTesting main.py integration...")
    
    try:
        # Test importing main.py
        import main
        print("✅ Main.py imports successfully with database module!")
        
        # Test that the init_db function is available
        from database import init_db
        print("✅ Database module functions are accessible!")
        
    except Exception as e:
        print(f"❌ Main.py integration test failed: {e}")

if __name__ == "__main__":
    test_database_module()
    test_main_integration()
    print("\n🎉 Database module tests completed!")