"""Mock data for testing purposes."""

# Sample questions for testing
SAMPLE_QUESTIONS = [
    {
        "id": 1,
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
        "id": 2,
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
        "id": 3,
        "text": "Which programming language is known for web development?",
        "options": [
            {"id": "a", "text": "Python"},
            {"id": "b", "text": "JavaScript"},
            {"id": "c", "text": "Java"},
            {"id": "d", "text": "C++"}
        ],
        "correct_answer": "b",
        "category": "programming"
    },
    {
        "id": 4,
        "text": "What is the largest planet in our solar system?",
        "options": [
            {"id": "a", "text": "Earth"},
            {"id": "b", "text": "Mars"},
            {"id": "c", "text": "Jupiter"},
            {"id": "d", "text": "Saturn"}
        ],
        "correct_answer": "c",
        "category": "science"
    }
]

# Sample AI-generated questions response
AI_GENERATED_QUESTIONS = [
    {
        "text": "What is machine learning?",
        "options": [
            {"id": "a", "text": "A type of computer hardware"},
            {"id": "b", "text": "A subset of artificial intelligence"},
            {"id": "c", "text": "A programming language"},
            {"id": "d", "text": "A database system"}
        ],
        "correct_answer": "b",
        "category": "technology"
    }
]

# Sample user answers for testing quiz logic
SAMPLE_USER_ANSWERS = [
    {"question_id": 1, "selected_answer": "c", "is_correct": True},
    {"question_id": 2, "selected_answer": "a", "is_correct": False},
    {"question_id": 3, "selected_answer": "b", "is_correct": True},
    {"question_id": 4, "selected_answer": "c", "is_correct": True}
]

# Sample quiz results
SAMPLE_QUIZ_RESULTS = {
    "total_questions": 4,
    "correct_answers": 3,
    "score_percentage": 75.0,
    "answers": SAMPLE_USER_ANSWERS
}

# Sample configuration data
SAMPLE_CONFIG = {
    "llm_provider": "openai",
    "openai_model": "gpt-3.5-turbo",
    "openai_api_key": "test-api-key",
    "ollama_model": "llama3.2",
    "ollama_host": "http://localhost:11434"
}

# Sample error responses
ERROR_RESPONSES = {
    "api_error": {"error": "Internal server error", "status_code": 500},
    "not_found": {"error": "Resource not found", "status_code": 404},
    "bad_request": {"error": "Bad request", "status_code": 400},
    "unauthorized": {"error": "Unauthorized", "status_code": 401}
}

# Test categories
TEST_CATEGORIES = ["geography", "math", "programming", "science", "technology", "history"]

# Sample logging configuration
SAMPLE_LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "handlers": {
        "file": {
            "filename": "test.log",
            "maxBytes": 1024000,
            "backupCount": 3
        },
        "console": {
            "stream": "stdout"
        }
    }
}