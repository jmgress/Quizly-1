import sqlite3
import json
import os
import logging

logger = logging.getLogger(__name__)

DATABASE_NAME = 'quiz.db'

def init_db():
    """Initializes the database and populates it with sample questions if it doesn't exist."""
    if os.path.exists(DATABASE_NAME):
        logger.info(f"Database '{DATABASE_NAME}' already exists. Skipping initialization.")
        return

    logger.info(f"Creating and initializing database '{DATABASE_NAME}'...")
    conn = sqlite3.connect(DATABASE_NAME)
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

    # Insert sample questions
    sample_questions = [
        # Geography
        {"text": "What is the capital of France?", "options": [{"id": "a", "text": "London"}, {"id": "b", "text": "Berlin"}, {"id": "c", "text": "Paris"}, {"id": "d", "text": "Madrid"}], "correct_answer": "c", "category": "geography"},
        {"text": "What is the largest ocean on Earth?", "options": [{"id": "a", "text": "Atlantic Ocean"}, {"id": "b", "text": "Indian Ocean"}, {"id": "c", "text": "Arctic Ocean"}, {"id": "d", "text": "Pacific Ocean"}], "correct_answer": "d", "category": "geography"},
        {"text": "Which river is the longest in the world?", "options": [{"id": "a", "text": "Amazon River"}, {"id": "b", "text": "Nile River"}, {"id": "c", "text": "Yangtze River"}, {"id": "d", "text": "Mississippi River"}], "correct_answer": "b", "category": "geography"},
        {"text": "Mount Everest is located in which mountain range?", "options": [{"id": "a", "text": "Andes"}, {"id": "b", "text": "Rockies"}, {"id": "c", "text": "Himalayas"}, {"id": "d", "text": "Alps"}], "correct_answer": "c", "category": "geography"},
        {"text": "What is the smallest continent by land area?", "options": [{"id": "a", "text": "Europe"}, {"id": "b", "text": "Australia"}, {"id": "c", "text": "Antarctica"}, {"id": "d", "text": "South America"}], "correct_answer": "b", "category": "geography"},

        # Science
        {"text": "Which planet is known as the Red Planet?", "options": [{"id": "a", "text": "Venus"}, {"id": "b", "text": "Mars"}, {"id": "c", "text": "Jupiter"}, {"id": "d", "text": "Saturn"}], "correct_answer": "b", "category": "science"},
        {"text": "What is the chemical symbol for water?", "options": [{"id": "a", "text": "O2"}, {"id": "b", "text": "CO2"}, {"id": "c", "text": "H2O"}, {"id": "d", "text": "NaCl"}], "correct_answer": "c", "category": "science"},
        {"text": "What force pulls objects towards the center of the Earth?", "options": [{"id": "a", "text": "Magnetism"}, {"id": "b", "text": "Friction"}, {"id": "c", "text": "Gravity"}, {"id": "d", "text": "Tension"}], "correct_answer": "c", "category": "science"},
        {"text": "What is the powerhouse of the cell?", "options": [{"id": "a", "text": "Nucleus"}, {"id": "b", "text": "Ribosome"}, {"id": "c", "text": "Mitochondrion"}, {"id": "d", "text": "Chloroplast"}], "correct_answer": "c", "category": "science"},
        {"text": "How many bones are in the adult human body?", "options": [{"id": "a", "text": "206"}, {"id": "b", "text": "201"}, {"id": "c", "text": "212"}, {"id": "d", "text": "198"}], "correct_answer": "a", "category": "science"},

        # Math
        {"text": "What is 2 + 2?", "options": [{"id": "a", "text": "3"}, {"id": "b", "text": "4"}, {"id": "c", "text": "5"}, {"id": "d", "text": "6"}], "correct_answer": "b", "category": "math"},
        {"text": "What is the value of Pi (to two decimal places)?", "options": [{"id": "a", "text": "3.12"}, {"id": "b", "text": "3.14"}, {"id": "c", "text": "3.16"}, {"id": "d", "text": "3.18"}], "correct_answer": "b", "category": "math"},
        {"text": "How many sides does a triangle have?", "options": [{"id": "a", "text": "3"}, {"id": "b", "text": "4"}, {"id": "c", "text": "5"}, {"id": "d", "text": "6"}], "correct_answer": "a", "category": "math"},
        {"text": "What is 10 multiplied by 5?", "options": [{"id": "a", "text": "40"}, {"id": "b", "text": "50"}, {"id": "c", "text": "60"}, {"id": "d", "text": "70"}], "correct_answer": "b", "category": "math"},
        {"text": "What is the square root of 64?", "options": [{"id": "a", "text": "6"}, {"id": "b", "text": "7"}, {"id": "c", "text": "8"}, {"id": "d", "text": "9"}], "correct_answer": "c", "category": "math"},

        # Literature
        {"text": "Who wrote 'Romeo and Juliet'?", "options": [{"id": "a", "text": "Charles Dickens"}, {"id": "b", "text": "William Shakespeare"}, {"id": "c", "text": "Jane Austen"}, {"id": "d", "text": "Mark Twain"}], "correct_answer": "b", "category": "literature"},
        {"text": "In 'The Hobbit', who is the protagonist?", "options": [{"id": "a", "text": "Gandalf"}, {"id": "b", "text": "Frodo Baggins"}, {"id": "c", "text": "Bilbo Baggins"}, {"id": "d", "text": "Gollum"}], "correct_answer": "c", "category": "literature"},
        {"text": "Which of these is a novel by George Orwell?", "options": [{"id": "a", "text": "Brave New World"}, {"id": "b", "text": "1984"}, {"id": "c", "text": "Fahrenheit 451"}, {"id": "d", "text": "The Handmaid's Tale"}], "correct_answer": "b", "category": "literature"},
        {"text": "Who is the author of the Harry Potter series?", "options": [{"id": "a", "text": "J.R.R. Tolkien"}, {"id": "b", "text": "George R.R. Martin"}, {"id": "c", "text": "J.K. Rowling"}, {"id": "d", "text": "Suzanne Collins"}], "correct_answer": "c", "category": "literature"},
        {"text": "What is the name of Captain Ahab's ship in 'Moby Dick'?", "options": [{"id": "a", "text": "The Pequod"}, {"id": "b", "text": "The Nautilus"}, {"id": "c", "text": "The Hispaniola"}, {"id": "d", "text": "The Jolly Roger"}], "correct_answer": "a", "category": "literature"},

        # General
        {"text": "What is the most spoken language in the world?", "options": [{"id": "a", "text": "Spanish"}, {"id": "b", "text": "Mandarin Chinese"}, {"id": "c", "text": "English"}, {"id": "d", "text": "Hindi"}], "correct_answer": "c", "category": "general"},
        {"text": "In which year did World War II end?", "options": [{"id": "a", "text": "1943"}, {"id": "b", "text": "1945"}, {"id": "c", "text": "1947"}, {"id": "d", "text": "1950"}], "correct_answer": "b", "category": "general"},
        {"text": "What is the currency of Japan?", "options": [{"id": "a", "text": "Yuan"}, {"id": "b", "text": "Won"}, {"id": "c", "text": "Yen"}, {"id": "d", "text": "Baht"}], "correct_answer": "c", "category": "general"},
        {"text": "Who painted the Mona Lisa?", "options": [{"id": "a", "text": "Vincent van Gogh"}, {"id": "b", "text": "Pablo Picasso"}, {"id": "c", "text": "Leonardo da Vinci"}, {"id": "d", "text": "Claude Monet"}], "correct_answer": "c", "category": "general"},
        {"text": "What is the capital of Australia?", "options": [{"id": "a", "text": "Sydney"}, {"id": "b", "text": "Melbourne"}, {"id": "c", "text": "Canberra"}, {"id": "d", "text": "Perth"}], "correct_answer": "c", "category": "general"},
    ]

    for q in sample_questions:
        cursor.execute(
            "INSERT INTO questions (text, options, correct_answer, category) VALUES (?, ?, ?, ?)",
            (q["text"], json.dumps(q["options"]), q["correct_answer"], q["category"])
        )

    conn.commit()
    conn.close()
    logger.info(f"Database '{DATABASE_NAME}' initialized successfully with {len(sample_questions)} sample questions.")

def get_db_connection():
    """Establishes a connection to the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn
