"""Shared test helpers for Python tests."""

import os
import sys
import tempfile
import json
import sqlite3
from typing import Dict, Any, List, Optional
from contextlib import contextmanager

# Add backend directory to path for imports
BACKEND_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
sys.path.insert(0, BACKEND_DIR)

class DatabaseTestHelper:
    """Helper class for database-related testing."""
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.connection = None
    
    def setup_test_database(self):
        """Set up a test database with sample data."""
        self.connection = sqlite3.connect(self.db_path)
        cursor = self.connection.cursor()
        
        # Create questions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                category TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create options table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS options (
                id TEXT NOT NULL,
                question_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                FOREIGN KEY (question_id) REFERENCES questions (id)
            )
        ''')
        
        # Insert sample data
        sample_questions = [
            (1, "What is the capital of France?", "geography", "c"),
            (2, "What is 2 + 2?", "math", "b"),
            (3, "Which language is used for web development?", "programming", "b")
        ]
        
        cursor.executemany(
            "INSERT OR REPLACE INTO questions (id, text, category, correct_answer) VALUES (?, ?, ?, ?)",
            sample_questions
        )
        
        sample_options = [
            ("a", 1, "London"),
            ("b", 1, "Berlin"),
            ("c", 1, "Paris"),
            ("d", 1, "Madrid"),
            ("a", 2, "3"),
            ("b", 2, "4"),
            ("c", 2, "5"),
            ("d", 2, "6"),
            ("a", 3, "Python"),
            ("b", 3, "JavaScript"),
            ("c", 3, "Java"),
            ("d", 3, "C++")
        ]
        
        cursor.executemany(
            "INSERT OR REPLACE INTO options (id, question_id, text) VALUES (?, ?, ?)",
            sample_options
        )
        
        self.connection.commit()
        return self.connection
    
    def cleanup(self):
        """Clean up database connection."""
        if self.connection:
            self.connection.close()
    
    def get_question_count(self) -> int:
        """Get total number of questions in database."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM questions")
        return cursor.fetchone()[0]
    
    def get_questions_by_category(self, category: str) -> List[Dict]:
        """Get questions for a specific category."""
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT id, text, category, correct_answer FROM questions WHERE category = ?",
            (category,)
        )
        questions = []
        for row in cursor.fetchall():
            question = {
                "id": row[0],
                "text": row[1],
                "category": row[2],
                "correct_answer": row[3]
            }
            
            # Get options for this question
            cursor.execute(
                "SELECT id, text FROM options WHERE question_id = ?",
                (question["id"],)
            )
            question["options"] = [
                {"id": opt_row[0], "text": opt_row[1]}
                for opt_row in cursor.fetchall()
            ]
            questions.append(question)
        
        return questions

class ConfigTestHelper:
    """Helper class for configuration testing."""
    
    @staticmethod
    def create_temp_config(config_data: Dict[str, Any] = None) -> str:
        """Create a temporary configuration file."""
        if config_data is None:
            config_data = {
                "llm_provider": "openai",
                "openai_model": "gpt-3.5-turbo",
                "openai_api_key": "test-key",
                "ollama_model": "llama3.2",
                "ollama_host": "http://localhost:11434"
            }
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(config_data, temp_file, indent=2)
        temp_file.close()
        return temp_file.name
    
    @staticmethod
    def cleanup_temp_config(config_path: str):
        """Remove temporary configuration file."""
        try:
            os.remove(config_path)
        except FileNotFoundError:
            pass

class APITestHelper:
    """Helper class for API testing."""
    
    @staticmethod
    def create_mock_response(data: Any, status_code: int = 200):
        """Create a mock HTTP response."""
        class MockResponse:
            def __init__(self, data, status_code):
                self.data = data
                self.status_code = status_code
            
            def json(self):
                return self.data
            
            def raise_for_status(self):
                if self.status_code >= 400:
                    raise Exception(f"HTTP {self.status_code} Error")
        
        return MockResponse(data, status_code)
    
    @staticmethod
    def validate_question_structure(question: Dict) -> bool:
        """Validate that a question has the required structure."""
        required_fields = ["text", "options", "correct_answer"]
        
        for field in required_fields:
            if field not in question:
                return False
        
        if not isinstance(question["options"], list) or len(question["options"]) == 0:
            return False
        
        for option in question["options"]:
            if "id" not in option or "text" not in option:
                return False
        
        # Check that correct_answer references a valid option
        option_ids = [opt["id"] for opt in question["options"]]
        if question["correct_answer"] not in option_ids:
            return False
        
        return True

class LoggingTestHelper:
    """Helper class for logging-related testing."""
    
    @staticmethod
    def create_temp_log_file() -> str:
        """Create a temporary log file for testing."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False)
        temp_file.close()
        return temp_file.name
    
    @staticmethod
    def cleanup_temp_log_file(log_path: str):
        """Remove temporary log file."""
        try:
            os.remove(log_path)
        except FileNotFoundError:
            pass
    
    @staticmethod
    def get_log_entries(log_path: str) -> List[str]:
        """Read log entries from a log file."""
        try:
            with open(log_path, 'r') as f:
                return f.readlines()
        except FileNotFoundError:
            return []

@contextmanager
def temporary_environment(**env_vars):
    """Context manager for temporarily setting environment variables."""
    old_environ = dict(os.environ)
    os.environ.update(env_vars)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)

def assert_quiz_score(answers: List[Dict], expected_score: float, tolerance: float = 0.01):
    """Assert that quiz score calculation is correct."""
    correct_count = sum(1 for answer in answers if answer.get("is_correct", False))
    total_count = len(answers)
    calculated_score = (correct_count / total_count) * 100 if total_count > 0 else 0
    
    assert abs(calculated_score - expected_score) < tolerance, \
        f"Expected score {expected_score}, got {calculated_score}"

def create_test_question(
    text: str = "Test question?",
    category: str = "test",
    correct_answer: str = "a",
    options: List[Dict] = None
) -> Dict:
    """Create a test question with default values."""
    if options is None:
        options = [
            {"id": "a", "text": "Option A"},
            {"id": "b", "text": "Option B"},
            {"id": "c", "text": "Option C"},
            {"id": "d", "text": "Option D"}
        ]
    
    return {
        "text": text,
        "category": category,
        "correct_answer": correct_answer,
        "options": options
    }

# Export commonly used helpers
__all__ = [
    'DatabaseTestHelper',
    'ConfigTestHelper', 
    'APITestHelper',
    'LoggingTestHelper',
    'temporary_environment',
    'assert_quiz_score',
    'create_test_question'
]