import os
import json
import sqlite3
import logging

# Use environment variable for DB path with fallback
DB_FILENAME = os.getenv("DATABASE_PATH", "quiz.db")
DB_PATH = os.path.join(os.path.dirname(__file__), DB_FILENAME)

logger = logging.getLogger(__name__)


def get_connection():
    """Return a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """Initialize the database with tables and sample data if needed."""
    if os.path.exists(DB_PATH):
        logger.info("Database already exists at %s, skipping initialization", DB_PATH)
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create questions table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            options TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            category TEXT DEFAULT 'general'
        )
        """
    )

    # Create quiz_sessions table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS quiz_sessions (
            id TEXT PRIMARY KEY,
            total_questions INTEGER,
            correct_answers INTEGER,
            score_percentage REAL,
            created_at TEXT,
            answers TEXT
        )
        """
    )

    # Sample questions: 5 per category
    sample_questions = [
        # Geography
        {
            "text": "What is the capital of France?",
            "options": [
                {"id": "a", "text": "London"},
                {"id": "b", "text": "Berlin"},
                {"id": "c", "text": "Paris"},
                {"id": "d", "text": "Madrid"}
            ],
            "correct_answer": "c",
            "category": "geography",
        },
        {
            "text": "Which river runs through Baghdad?",
            "options": [
                {"id": "a", "text": "Nile"},
                {"id": "b", "text": "Tigris"},
                {"id": "c", "text": "Amazon"},
                {"id": "d", "text": "Danube"}
            ],
            "correct_answer": "b",
            "category": "geography",
        },
        {
            "text": "Mount Everest is part of which mountain range?",
            "options": [
                {"id": "a", "text": "Alps"},
                {"id": "b", "text": "Andes"},
                {"id": "c", "text": "Himalayas"},
                {"id": "d", "text": "Rockies"}
            ],
            "correct_answer": "c",
            "category": "geography",
        },
        {
            "text": "Which continent contains the Sahara Desert?",
            "options": [
                {"id": "a", "text": "Africa"},
                {"id": "b", "text": "Asia"},
                {"id": "c", "text": "South America"},
                {"id": "d", "text": "Australia"}
            ],
            "correct_answer": "a",
            "category": "geography",
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
            "category": "geography",
        },
        # Science
        {
            "text": "Which planet is known as the Red Planet?",
            "options": [
                {"id": "a", "text": "Venus"},
                {"id": "b", "text": "Mars"},
                {"id": "c", "text": "Jupiter"},
                {"id": "d", "text": "Saturn"}
            ],
            "correct_answer": "b",
            "category": "science",
        },
        {
            "text": "What gas do plants absorb from the atmosphere?",
            "options": [
                {"id": "a", "text": "Oxygen"},
                {"id": "b", "text": "Carbon dioxide"},
                {"id": "c", "text": "Nitrogen"},
                {"id": "d", "text": "Hydrogen"}
            ],
            "correct_answer": "b",
            "category": "science",
        },
        {
            "text": "What is the chemical symbol for gold?",
            "options": [
                {"id": "a", "text": "Au"},
                {"id": "b", "text": "Ag"},
                {"id": "c", "text": "Fe"},
                {"id": "d", "text": "O"}
            ],
            "correct_answer": "a",
            "category": "science",
        },
        {
            "text": "Who developed the theory of relativity?",
            "options": [
                {"id": "a", "text": "Isaac Newton"},
                {"id": "b", "text": "Nikola Tesla"},
                {"id": "c", "text": "Albert Einstein"},
                {"id": "d", "text": "Marie Curie"}
            ],
            "correct_answer": "c",
            "category": "science",
        },
        {
            "text": "How many bones are in the adult human body?",
            "options": [
                {"id": "a", "text": "196"},
                {"id": "b", "text": "206"},
                {"id": "c", "text": "216"},
                {"id": "d", "text": "226"}
            ],
            "correct_answer": "b",
            "category": "science",
        },
        # Math
        {
            "text": "What is 2 + 2?",
            "options": [
                {"id": "a", "text": "3"},
                {"id": "b", "text": "4"},
                {"id": "c", "text": "5"},
                {"id": "d", "text": "6"}
            ],
            "correct_answer": "b",
            "category": "math",
        },
        {
            "text": "What is the value of \u03c0 rounded to two decimal places?",
            "options": [
                {"id": "a", "text": "2.72"},
                {"id": "b", "text": "3.14"},
                {"id": "c", "text": "1.62"},
                {"id": "d", "text": "3.41"}
            ],
            "correct_answer": "b",
            "category": "math",
        },
        {
            "text": "Solve for x: 3x = 12.",
            "options": [
                {"id": "a", "text": "3"},
                {"id": "b", "text": "4"},
                {"id": "c", "text": "6"},
                {"id": "d", "text": "9"}
            ],
            "correct_answer": "b",
            "category": "math",
        },
        {
            "text": "What is the square root of 81?",
            "options": [
                {"id": "a", "text": "7"},
                {"id": "b", "text": "8"},
                {"id": "c", "text": "9"},
                {"id": "d", "text": "10"}
            ],
            "correct_answer": "c",
            "category": "math",
        },
        {
            "text": "How many degrees are in a right angle?",
            "options": [
                {"id": "a", "text": "45"},
                {"id": "b", "text": "90"},
                {"id": "c", "text": "180"},
                {"id": "d", "text": "360"}
            ],
            "correct_answer": "b",
            "category": "math",
        },
        # Literature
        {
            "text": "Who wrote 'Romeo and Juliet'?",
            "options": [
                {"id": "a", "text": "Charles Dickens"},
                {"id": "b", "text": "William Shakespeare"},
                {"id": "c", "text": "Jane Austen"},
                {"id": "d", "text": "Mark Twain"}
            ],
            "correct_answer": "b",
            "category": "literature",
        },
        {
            "text": "Who is the author of '1984'?",
            "options": [
                {"id": "a", "text": "George Orwell"},
                {"id": "b", "text": "Aldous Huxley"},
                {"id": "c", "text": "J.K. Rowling"},
                {"id": "d", "text": "Ernest Hemingway"}
            ],
            "correct_answer": "a",
            "category": "literature",
        },
        {
            "text": "'Moby-Dick' was written by which author?",
            "options": [
                {"id": "a", "text": "Herman Melville"},
                {"id": "b", "text": "F. Scott Fitzgerald"},
                {"id": "c", "text": "John Steinbeck"},
                {"id": "d", "text": "Jules Verne"}
            ],
            "correct_answer": "a",
            "category": "literature",
        },
        {
            "text": "The novel 'Pride and Prejudice' was written by?",
            "options": [
                {"id": "a", "text": "Emily Bront\u00eb"},
                {"id": "b", "text": "Jane Austen"},
                {"id": "c", "text": "Virginia Woolf"},
                {"id": "d", "text": "Mary Shelley"}
            ],
            "correct_answer": "b",
            "category": "literature",
        },
        {
            "text": "The 'Iliad' and the 'Odyssey' are epic poems by?",
            "options": [
                {"id": "a", "text": "Homer"},
                {"id": "b", "text": "Sophocles"},
                {"id": "c", "text": "Virgil"},
                {"id": "d", "text": "Ovid"}
            ],
            "correct_answer": "a",
            "category": "literature",
        },
        # General
        {
            "text": "Who painted the Mona Lisa?",
            "options": [
                {"id": "a", "text": "Vincent van Gogh"},
                {"id": "b", "text": "Pablo Picasso"},
                {"id": "c", "text": "Leonardo da Vinci"},
                {"id": "d", "text": "Claude Monet"}
            ],
            "correct_answer": "c",
            "category": "general",
        },
        {
            "text": "What is the tallest land mammal?",
            "options": [
                {"id": "a", "text": "Elephant"},
                {"id": "b", "text": "Giraffe"},
                {"id": "c", "text": "Rhinoceros"},
                {"id": "d", "text": "Polar Bear"}
            ],
            "correct_answer": "b",
            "category": "general",
        },
        {
            "text": "In computing, what does CPU stand for?",
            "options": [
                {"id": "a", "text": "Central Processing Unit"},
                {"id": "b", "text": "Computer Personal Unit"},
                {"id": "c", "text": "Central Performance Utility"},
                {"id": "d", "text": "Core Processing Unit"}
            ],
            "correct_answer": "a",
            "category": "general",
        },
        {
            "text": "How many continents are there on Earth?",
            "options": [
                {"id": "a", "text": "Five"},
                {"id": "b", "text": "Six"},
                {"id": "c", "text": "Seven"},
                {"id": "d", "text": "Eight"}
            ],
            "correct_answer": "c",
            "category": "general",
        },
        {
            "text": "What is the boiling point of water at sea level in Celsius?",
            "options": [
                {"id": "a", "text": "90"},
                {"id": "b", "text": "95"},
                {"id": "c", "text": "100"},
                {"id": "d", "text": "105"}
            ],
            "correct_answer": "c",
            "category": "general",
        },
    ]

    for q in sample_questions:
        cursor.execute(
            "INSERT INTO questions (text, options, correct_answer, category) VALUES (?, ?, ?, ?)",
            (q["text"], json.dumps(q["options"]), q["correct_answer"], q["category"]),
        )

    conn.commit()
    conn.close()
    logger.info("Database initialized with sample data at %s", DB_PATH)
