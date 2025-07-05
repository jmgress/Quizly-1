from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import LLM providers
from llm_providers import create_llm_provider, get_available_providers
from database import init_db, get_connection

import logging
logging.basicConfig(level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")))
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

# Initialize database when the module is imported
init_db()


@app.get("/")
def read_root():
    return {"message": "Welcome to Quizly API"}

@app.get("/api/questions", response_model=List[Question])
def get_questions(category: Optional[str] = None, limit: Optional[int] = 10):
    """Get quiz questions, optionally filtered by category"""
    conn = get_connection()
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
    conn = get_connection()
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
    conn = get_connection()
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
    conn = get_connection()
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
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT category FROM questions")
    categories = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return {"categories": categories}

@app.get("/api/llm/health")
def check_llm_health():
    """Check the health of the configured LLM provider"""
    try:
        provider = create_llm_provider()
        is_healthy = provider.health_check()
        provider_type = os.getenv("LLM_PROVIDER", "ollama").lower()
        
        return {
            "provider": provider_type,
            "healthy": is_healthy,
            "available_providers": get_available_providers()
        }
    except Exception as e:
        logger.error(f"LLM health check failed: {str(e)}")
        return {
            "provider": os.getenv("LLM_PROVIDER", "ollama").lower(),
            "healthy": False,
            "error": str(e),
            "available_providers": []
        }


@app.get("/api/questions/ai", response_model=List[Question])
def generate_ai_questions(subject: str, limit: Optional[int] = 5, provider_type: Optional[str] = None, model: Optional[str] = None):
    """Generate AI-powered questions for a specific subject using configured LLM provider"""
    try:
        # Get default limit from environment if not provided
        if limit is None:
            limit = int(os.getenv("DEFAULT_QUESTION_LIMIT", "5"))
        
        # Use provider from environment or query parameter
        provider_type = provider_type or os.getenv("LLM_PROVIDER", "ollama").lower()
        
        # Ensure model is properly set based on provider type
        if provider_type == "openai":
            used_model = model or os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        else:
            used_model = model or os.getenv('OLLAMA_MODEL', 'llama3.2')
        
        provider = create_llm_provider(provider_type, model=used_model)
        
        # Log the provider and model being used
        if provider_type == "openai":
            logger.info(f"Using OpenAI model: {used_model}")
        else:
            logger.info(f"Using provider: {provider_type} model: {used_model}")
        
        # Generate questions using the provider
        questions = provider.generate_questions(subject, limit)
        
        logger.info(f"Generated {len(questions)} AI questions for subject: {subject} using {provider_type} provider")
        return questions
        
    except Exception as e:
        logger.error(f"AI question generation failed: {str(e)}")
        # Return provider-specific error message
        error_msg = f"{provider_type.capitalize() if provider_type else 'LLM'} question generation failed: {str(e)}."
        
        if provider_type == "openai":
            error_msg += " Please check your OpenAI API key and quota."
        elif provider_type == "ollama":
            error_msg += " Please check if Ollama is running locally."
        
        raise HTTPException(status_code=503, detail=error_msg)

@app.get("/api/llm/providers")
def get_llm_providers():
    """Get list of available LLM providers"""
    providers = get_available_providers()
    current_provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    
    return {
        "current": current_provider,
        "available": providers
    }


@app.get("/api/models")
def get_models(provider: Optional[str] = None):
    """Get list of available models for a provider"""
    provider_type = provider or os.getenv("LLM_PROVIDER", "ollama").lower()
    from llm_providers import get_available_models

    models = get_available_models(provider_type)
    return {"provider": provider_type, "models": models}

if __name__ == "__main__":
    import uvicorn
    
    # Initialize database
    init_db()
    
    # Get host and port from environment
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    
    # Log provider configuration
    provider_type = os.getenv("LLM_PROVIDER", "ollama").lower()
    logger.info(f"Starting Quizly API server with LLM provider: {provider_type}")
    
    if provider_type == "openai":
        logger.info(f"OpenAI model: {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}")
    elif provider_type == "ollama":
        logger.info(f"Ollama model: {os.getenv('OLLAMA_MODEL', 'llama3.2')}")
        logger.info(f"Ollama host: {os.getenv('OLLAMA_HOST', 'http://localhost:11434')}")
    
    # Start server
    uvicorn.run(app, host=host, port=port)
