"""
Database initialization module for Quizly application.

This module handles database setup, table creation, and sample data insertion.
"""

import sqlite3
import json
import os
import logging

# Set up logging
logger = logging.getLogger("database") # Use component-specific logger

def init_db():
    """
    Initialize the database with tables and sample data.
    
    Only initializes if quiz.db file doesn't exist to preserve existing data.
    Logs initialization status for debugging.
    """
    db_path = 'quiz.db'
    
    # Check if database file exists
    if os.path.exists(db_path):
        logger.info("Database file already exists, skipping initialization")
        return
    
    logger.info("Database file not found, initializing new database")
    
    conn = sqlite3.connect(db_path)
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
    
    # Create quiz_sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_sessions (
            id TEXT PRIMARY KEY,
            total_questions INTEGER,
            correct_answers INTEGER,
            score_percentage REAL,
            created_at TEXT,
            answers TEXT
        )
    ''')
    
    # Insert sample questions - 5 per category (25 total)
    cursor.execute("SELECT COUNT(*) FROM questions")
    if cursor.fetchone()[0] == 0:
        sample_questions = [
            # Geography questions (5)
            {
                "text": "What is the capital of France?",
                "options": [
                    {"id": "a", "text": "London"},
                    {"id": "b", "text": "Berlin"}, 
                    {"id": "c", "text": "Paris"},
                    {"id": "d", "text": "Madrid"}
                ],
                "correct_answer": "c",
                "category": "geography"
            },
            {
                "text": "What is the largest ocean on Earth?",
                "options": [
                    {"id": "a", "text": "Atlantic Ocean"},
                    {"id": "b", "text": "Indian Ocean"},
                    {"id": "c", "text": "Arctic Ocean"},
                    {"id": "d", "text": "Pacific Ocean"}
                ],
                "correct_answer": "d",
                "category": "geography"
            },
            {
                "text": "Which continent is known as the 'Dark Continent'?",
                "options": [
                    {"id": "a", "text": "Asia"},
                    {"id": "b", "text": "Africa"},
                    {"id": "c", "text": "South America"},
                    {"id": "d", "text": "Australia"}
                ],
                "correct_answer": "b",
                "category": "geography"
            },
            {
                "text": "What is the longest river in the world?",
                "options": [
                    {"id": "a", "text": "Amazon River"},
                    {"id": "b", "text": "Nile River"},
                    {"id": "c", "text": "Mississippi River"},
                    {"id": "d", "text": "Yangtze River"}
                ],
                "correct_answer": "b",
                "category": "geography"
            },
            {
                "text": "Which mountain range contains Mount Everest?",
                "options": [
                    {"id": "a", "text": "Rocky Mountains"},
                    {"id": "b", "text": "Andes Mountains"},
                    {"id": "c", "text": "Himalayas"},
                    {"id": "d", "text": "Alps"}
                ],
                "correct_answer": "c",
                "category": "geography"
            },
            
            # Science questions (5)
            {
                "text": "Which planet is known as the Red Planet?",
                "options": [
                    {"id": "a", "text": "Venus"},
                    {"id": "b", "text": "Mars"},
                    {"id": "c", "text": "Jupiter"},
                    {"id": "d", "text": "Saturn"}
                ],
                "correct_answer": "b",
                "category": "science"
            },
            {
                "text": "What is the chemical symbol for gold?",
                "options": [
                    {"id": "a", "text": "Go"},
                    {"id": "b", "text": "Gd"},
                    {"id": "c", "text": "Au"},
                    {"id": "d", "text": "Ag"}
                ],
                "correct_answer": "c",
                "category": "science"
            },
            {
                "text": "How many bones are in the adult human body?",
                "options": [
                    {"id": "a", "text": "206"},
                    {"id": "b", "text": "208"},
                    {"id": "c", "text": "210"},
                    {"id": "d", "text": "212"}
                ],
                "correct_answer": "a",
                "category": "science"
            },
            {
                "text": "What is the powerhouse of the cell?",
                "options": [
                    {"id": "a", "text": "Nucleus"},
                    {"id": "b", "text": "Ribosome"},
                    {"id": "c", "text": "Mitochondria"},
                    {"id": "d", "text": "Golgi apparatus"}
                ],
                "correct_answer": "c",
                "category": "science"
            },
            {
                "text": "What gas do plants absorb from the atmosphere during photosynthesis?",
                "options": [
                    {"id": "a", "text": "Oxygen"},
                    {"id": "b", "text": "Carbon dioxide"},
                    {"id": "c", "text": "Nitrogen"},
                    {"id": "d", "text": "Hydrogen"}
                ],
                "correct_answer": "b",
                "category": "science"
            },
            
            # Math questions (5)
            {
                "text": "What is 2 + 2?",
                "options": [
                    {"id": "a", "text": "3"},
                    {"id": "b", "text": "4"},
                    {"id": "c", "text": "5"},
                    {"id": "d", "text": "6"}
                ],
                "correct_answer": "b",
                "category": "math"
            },
            {
                "text": "What is the square root of 64?",
                "options": [
                    {"id": "a", "text": "6"},
                    {"id": "b", "text": "7"},
                    {"id": "c", "text": "8"},
                    {"id": "d", "text": "9"}
                ],
                "correct_answer": "c",
                "category": "math"
            },
            {
                "text": "What is 15% of 200?",
                "options": [
                    {"id": "a", "text": "25"},
                    {"id": "b", "text": "30"},
                    {"id": "c", "text": "35"},
                    {"id": "d", "text": "40"}
                ],
                "correct_answer": "b",
                "category": "math"
            },
            {
                "text": "What is the value of π (pi) to two decimal places?",
                "options": [
                    {"id": "a", "text": "3.14"},
                    {"id": "b", "text": "3.15"},
                    {"id": "c", "text": "3.16"},
                    {"id": "d", "text": "3.17"}
                ],
                "correct_answer": "a",
                "category": "math"
            },
            {
                "text": "If a triangle has angles of 60°, 60°, and 60°, what type of triangle is it?",
                "options": [
                    {"id": "a", "text": "Right triangle"},
                    {"id": "b", "text": "Isosceles triangle"},
                    {"id": "c", "text": "Equilateral triangle"},
                    {"id": "d", "text": "Scalene triangle"}
                ],
                "correct_answer": "c",
                "category": "math"
            },
            
            # Literature questions (5)
            {
                "text": "Who wrote 'Romeo and Juliet'?",
                "options": [
                    {"id": "a", "text": "Charles Dickens"},
                    {"id": "b", "text": "William Shakespeare"},
                    {"id": "c", "text": "Jane Austen"},
                    {"id": "d", "text": "Mark Twain"}
                ],
                "correct_answer": "b",
                "category": "literature"
            },
            {
                "text": "Which novel begins with 'It was the best of times, it was the worst of times'?",
                "options": [
                    {"id": "a", "text": "Great Expectations"},
                    {"id": "b", "text": "Oliver Twist"},
                    {"id": "c", "text": "A Tale of Two Cities"},
                    {"id": "d", "text": "David Copperfield"}
                ],
                "correct_answer": "c",
                "category": "literature"
            },
            {
                "text": "Who wrote the Harry Potter series?",
                "options": [
                    {"id": "a", "text": "J.R.R. Tolkien"},
                    {"id": "b", "text": "C.S. Lewis"},
                    {"id": "c", "text": "J.K. Rowling"},
                    {"id": "d", "text": "Roald Dahl"}
                ],
                "correct_answer": "c",
                "category": "literature"
            },
            {
                "text": "In which Shakespeare play does the character Hamlet appear?",
                "options": [
                    {"id": "a", "text": "Macbeth"},
                    {"id": "b", "text": "Hamlet"},
                    {"id": "c", "text": "King Lear"},
                    {"id": "d", "text": "Othello"}
                ],
                "correct_answer": "b",
                "category": "literature"
            },
            {
                "text": "Who wrote '1984'?",
                "options": [
                    {"id": "a", "text": "Aldous Huxley"},
                    {"id": "b", "text": "Ray Bradbury"},
                    {"id": "c", "text": "George Orwell"},
                    {"id": "d", "text": "Kurt Vonnegut"}
                ],
                "correct_answer": "c",
                "category": "literature"
            },
            
            # General questions (5)
            {
                "text": "What is the largest mammal in the world?",
                "options": [
                    {"id": "a", "text": "African Elephant"},
                    {"id": "b", "text": "Blue Whale"},
                    {"id": "c", "text": "Giraffe"},
                    {"id": "d", "text": "Polar Bear"}
                ],
                "correct_answer": "b",
                "category": "general"
            },
            {
                "text": "How many days are there in a leap year?",
                "options": [
                    {"id": "a", "text": "365"},
                    {"id": "b", "text": "366"},
                    {"id": "c", "text": "367"},
                    {"id": "d", "text": "364"}
                ],
                "correct_answer": "b",
                "category": "general"
            },
            {
                "text": "What is the hardest natural substance on Earth?",
                "options": [
                    {"id": "a", "text": "Gold"},
                    {"id": "b", "text": "Iron"},
                    {"id": "c", "text": "Diamond"},
                    {"id": "d", "text": "Platinum"}
                ],
                "correct_answer": "c",
                "category": "general"
            },
            {
                "text": "Which instrument is used to measure temperature?",
                "options": [
                    {"id": "a", "text": "Barometer"},
                    {"id": "b", "text": "Thermometer"},
                    {"id": "c", "text": "Hygrometer"},
                    {"id": "d", "text": "Anemometer"}
                ],
                "correct_answer": "b",
                "category": "general"
            },
            {
                "text": "What is the currency of Japan?",
                "options": [
                    {"id": "a", "text": "Yuan"},
                    {"id": "b", "text": "Won"},
                    {"id": "c", "text": "Yen"},
                    {"id": "d", "text": "Rupee"}
                ],
                "correct_answer": "c",
                "category": "general"
            }
        ]
        
        for q in sample_questions:
            cursor.execute(
                "INSERT INTO questions (text, options, correct_answer, category) VALUES (?, ?, ?, ?)",
                (q["text"], json.dumps(q["options"]), q["correct_answer"], q["category"])
            )
        
        logger.info(f"Inserted {len(sample_questions)} sample questions into database")
    
    conn.commit()
    conn.close()
    logger.info("Database initialization completed successfully")