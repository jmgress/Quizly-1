from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import json
import uuid
from datetime import datetime
import logging
from dotenv import load_dotenv
import os
# Remove direct ollama import if no longer used directly in main.py
# import ollama

# Import provider factory and custom exceptions
from backend.llm_providers import get_llm_provider, LLMProviderError, LLMConnectionError, LLMAPIError

# Load environment variables from .env file
load_dotenv()

# Setup basic logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)
# BasicConfig can be called only once. If llm_providers also calls it, it might be an issue.
# Let's ensure logging is configured once, or rely on FastAPI's default logging/uvicorn.
# For now, assume llm_providers' logger will work. If main needs its own, configure carefully.
# Re-evaluating: llm_providers uses getLogger, doesn't configure basicConfig. So this is fine.
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper(), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


app = FastAPI(title="Quizly API", description="Knowledge Testing Application API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class QuestionOption(BaseModel):
    id: str
    text: str

class Question(BaseModel):
    id: int
    text: str
    options: List[QuestionOption]
    correct_answer: str
    category: Optional[str] = "general"

class QuestionUpdate(BaseModel):
    text: Optional[str] = None
    options: Optional[List[QuestionOption]] = None
    correct_answer: Optional[str] = None
    category: Optional[str] = None

class QuizAnswer(BaseModel):
    question_id: int
    selected_answer: str
    correct_answer: Optional[str] = None

class QuizSubmission(BaseModel):
    answers: List[QuizAnswer]

class QuizResult(BaseModel):
    quiz_id: str
    total_questions: int
    correct_answers: int
    score_percentage: float
    answers: List[dict]

# Database initialization
def init_db():
    conn = sqlite3.connect('quiz.db')
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
    
    # Insert sample questions if table is empty
    cursor.execute("SELECT COUNT(*) FROM questions")
    if cursor.fetchone()[0] == 0:
        sample_questions = [
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
                "text": "What is the largest ocean on Earth?",
                "options": [
                    {"id": "a", "text": "Atlantic Ocean"},
                    {"id": "b", "text": "Indian Ocean"},
                    {"id": "c", "text": "Arctic Ocean"},
                    {"id": "d", "text": "Pacific Ocean"}
                ],
                "correct_answer": "d",
                "category": "geography"
            }
        ]
        
        for q in sample_questions:
            cursor.execute(
                "INSERT INTO questions (text, options, correct_answer, category) VALUES (?, ?, ?, ?)",
                (q["text"], json.dumps(q["options"]), q["correct_answer"], q["category"])
            )
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

@app.get("/")
def read_root():
    return {"message": "Welcome to Quizly API"}

@app.get("/api/questions", response_model=List[Question])
def get_questions(category: Optional[str] = None, limit: Optional[int] = 10):
    """Get quiz questions, optionally filtered by category"""
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    
    if category:
        cursor.execute("SELECT * FROM questions WHERE category = ? ORDER BY RANDOM() LIMIT ?", (category, limit))
    else:
        # For admin interface, allow fetching all questions by setting a high limit
        if limit and limit > 1000:
            cursor.execute("SELECT * FROM questions ORDER BY id")
        else:
            cursor.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT ?", (limit,))
    
    questions = []
    for row in cursor.fetchall():
        questions.append({
            "id": row[0],
            "text": row[1],
            "options": json.loads(row[2]),
            "correct_answer": row[3],
            "category": row[4]
        })
    
    conn.close()
    return questions

@app.post("/api/quiz/submit", response_model=QuizResult)
def submit_quiz(submission: QuizSubmission):
    """Submit quiz answers and get results"""
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    
    # Get correct answers for submitted questions
    question_ids = [answer.question_id for answer in submission.answers]
    placeholders = ','.join(['?'] * len(question_ids)) if question_ids else ''
    db_correct_answers = {}
    if placeholders:
        cursor.execute(
            f"SELECT id, correct_answer FROM questions WHERE id IN ({placeholders})",
            question_ids
        )
        db_correct_answers = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Calculate score
    correct_count = 0
    answer_details = []

    for answer in submission.answers:
        correct_answer = db_correct_answers.get(answer.question_id) or answer.correct_answer
        is_correct = correct_answer == answer.selected_answer
        if is_correct:
            correct_count += 1

        answer_details.append({
            "question_id": answer.question_id,
            "selected_answer": answer.selected_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct
        })
    
    total_questions = len(submission.answers)
    score_percentage = (correct_count / total_questions) * 100 if total_questions > 0 else 0
    
    # Save quiz session
    quiz_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO quiz_sessions (id, total_questions, correct_answers, score_percentage, created_at, answers) VALUES (?, ?, ?, ?, ?, ?)",
        (quiz_id, total_questions, correct_count, score_percentage, datetime.now().isoformat(), json.dumps(answer_details))
    )
    
    conn.commit()
    conn.close()
    
    return QuizResult(
        quiz_id=quiz_id,
        total_questions=total_questions,
        correct_answers=correct_count,
        score_percentage=score_percentage,
        answers=answer_details
    )

@app.get("/api/quiz/{quiz_id}", response_model=QuizResult)
def get_quiz_result(quiz_id: str):
    """Get quiz results by ID"""
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM quiz_sessions WHERE id = ?", (quiz_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Quiz session not found")
    
    conn.close()
    
    return QuizResult(
        quiz_id=row[0],
        total_questions=row[1],
        correct_answers=row[2],
        score_percentage=row[3],
        answers=json.loads(row[5])
    )

@app.put("/api/questions/{question_id}", response_model=Question)
def update_question(question_id: int, question_update: QuestionUpdate):
    """Update a question's fields"""
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    
    # First, check if the question exists
    cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Get current question data
    current_question = {
        "id": row[0],
        "text": row[1],
        "options": json.loads(row[2]),
        "correct_answer": row[3],
        "category": row[4]
    }
    
    # Update only provided fields
    update_data = {}
    if question_update.text is not None:
        update_data["text"] = question_update.text
    if question_update.options is not None:
        # Validate options format
        if len(question_update.options) != 4:
            raise HTTPException(status_code=400, detail="Question must have exactly 4 options")
        option_ids = [opt.id for opt in question_update.options]
        if len(set(option_ids)) != 4 or not all(id in ['a', 'b', 'c', 'd'] for id in option_ids):
            raise HTTPException(status_code=400, detail="Options must have unique IDs 'a', 'b', 'c', 'd'")
        update_data["options"] = json.dumps([{"id": opt.id, "text": opt.text} for opt in question_update.options])
    if question_update.correct_answer is not None:
        # Validate correct answer
        if question_update.options:
            valid_ids = [opt.id for opt in question_update.options]
        else:
            valid_ids = [opt["id"] for opt in current_question["options"]]
        if question_update.correct_answer not in valid_ids:
            raise HTTPException(status_code=400, detail="Correct answer must be one of the option IDs")
        update_data["correct_answer"] = question_update.correct_answer
    if question_update.category is not None:
        update_data["category"] = question_update.category
    
    # Build dynamic UPDATE query
    if update_data:
        set_clause = ", ".join([f"{key} = ?" for key in update_data.keys()])
        query = f"UPDATE questions SET {set_clause} WHERE id = ?"
        values = list(update_data.values()) + [question_id]
        cursor.execute(query, values)
        conn.commit()
    
    # Return updated question
    cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
    row = cursor.fetchone()
    conn.close()
    
    return {
        "id": row[0],
        "text": row[1],
        "options": json.loads(row[2]),
        "correct_answer": row[3],
        "category": row[4]
    }

@app.get("/api/categories")
def get_categories():
    """Get available quiz categories"""
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT category FROM questions")
    categories = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return {"categories": categories}

@app.get("/api/questions/ai", response_model=List[Question])
def generate_ai_questions(subject: str, limit: Optional[int] = 5):
    """Generate AI-powered questions for a specific subject using the configured LLM provider."""
    try:
        logger.info(f"Received request to generate {limit} AI questions for subject: {subject}")
        provider = get_llm_provider()
        
        # The prompt template is now handled by the provider, using PROMPT_TEMPLATE env var.
        # The provider's generate_questions method is expected to return a list of dicts
        # matching the structure needed, but without the 'id' field yet.
        generated_questions_data = provider.generate_questions(subject=subject, limit=limit)

        if not generated_questions_data:
            logger.warning(f"AI provider returned no questions for subject '{subject}'.")
            # Return empty list or raise error? For now, empty list to match previous behavior of returning [] if parsing failed.
            # This could also be an HTTPException 500 or 503 if it's unexpected.
            # Let's make it an error if nothing comes back, as it implies an issue.
            raise HTTPException(
                status_code=503,
                detail=f"AI provider returned no valid questions for subject '{subject}'. Check provider logs."
            )

        questions_with_ids = []
        for i, q_data in enumerate(generated_questions_data):
            # Basic validation, though provider should do most of this.
            if not all(key in q_data for key in ['text', 'options', 'correct_answer', 'category']):
                logger.warning(f"Provider returned incomplete question data: {q_data}. Skipping.")
                continue
            
            questions_with_ids.append({
                "id": 1000 + i,  # Use high IDs to avoid conflicts with DB questions, same as before
                "text": q_data["text"],
                "options": q_data["options"],
                "correct_answer": q_data["correct_answer"],
                "category": q_data["category"] # Category should now be set by the provider
            })
        
        if not questions_with_ids:
             logger.error(f"No questions could be formatted after generation for subject '{subject}'. Provider might have returned malformed data.")
             raise HTTPException(
                status_code=500,
                detail="Failed to format questions from AI provider. Check server logs."
            )

        logger.info(f"Successfully generated {len(questions_with_ids)} AI questions for subject: {subject}")
        return questions_with_ids

    except LLMConnectionError as e:
        logger.error(f"LLM Connection Error: {e}")
        raise HTTPException(status_code=503, detail=f"AI service connection error: {str(e)}")
    except LLMAPIError as e:
        logger.error(f"LLM API Error: {e}")
        raise HTTPException(status_code=502, detail=f"AI service API error: {str(e)}")
    except LLMProviderError as e: # Catchall for other provider errors
        logger.error(f"LLM Provider Error: {e}")
        raise HTTPException(status_code=500, detail=f"AI service provider error: {str(e)}")
    except ValueError as e: # Catch ValueErrors from factory (e.g. missing API key)
        logger.error(f"Configuration error for AI provider: {e}")
        raise HTTPException(status_code=400, detail=f"Configuration error: {str(e)}")
    except Exception as e:
        logger.exception(f"Unexpected error during AI question generation for subject '{subject}': {e}") #.exception includes stack trace
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during AI question generation: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)