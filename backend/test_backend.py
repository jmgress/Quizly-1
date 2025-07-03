#!/usr/bin/env python3

# Test script to check basic functionality
import sqlite3
import json
import uuid
from datetime import datetime

def test_database():
    """Test database functionality"""
    print("Testing database setup...")
    
    # Initialize database
    conn = sqlite3.connect('/tmp/test_quiz.db')
    cursor = conn.cursor()
    
    # Create questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            options TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            category TEXT DEFAULT 'general'
        )
    ''')
    
    # Insert sample question
    sample_question = {
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
    
    cursor.execute(
        "INSERT INTO questions (text, options, correct_answer, category) VALUES (?, ?, ?, ?)",
        (sample_question["text"], json.dumps(sample_question["options"]), 
         sample_question["correct_answer"], sample_question["category"])
    )
    
    # Test retrieval
    cursor.execute("SELECT * FROM questions")
    row = cursor.fetchone()
    
    if row:
        print("✅ Database test passed!")
        print(f"Sample question: {row[1]}")
        print(f"Options: {json.loads(row[2])}")
        print(f"Correct answer: {row[3]}")
    else:
        print("❌ Database test failed!")
    
    conn.commit()
    conn.close()

def test_quiz_logic():
    """Test quiz scoring logic"""
    print("\nTesting quiz scoring logic...")
    
    # Sample answers
    answers = [
        {"question_id": 1, "selected_answer": "c", "correct_answer": "c"},  # Correct
        {"question_id": 2, "selected_answer": "a", "correct_answer": "b"},  # Incorrect
    ]

    correct_answers_map = {1: "c", 2: "b"}
    
    correct_count = 0
    for answer in answers:
        if correct_answers_map.get(answer["question_id"]) == answer["selected_answer"]:
            correct_count += 1
    
    total_questions = len(answers)
    score_percentage = (correct_count / total_questions) * 100
    
    print(f"Correct answers: {correct_count}/{total_questions}")
    print(f"Score: {score_percentage}%")
    
    if score_percentage == 50.0:  # Expected score
        print("✅ Quiz logic test passed!")
    else:
        print("❌ Quiz logic test failed!")

if __name__ == "__main__":
    test_database()
    test_quiz_logic()
    print("\n🎉 All tests completed!")
