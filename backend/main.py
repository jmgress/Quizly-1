from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import json
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import LLM providers
from llm_providers import create_llm_provider, get_available_providers

# Import database module
from database import init_db

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

class LLMConfig(BaseModel):
    provider: str
    model: str

# Configuration file path
LLM_CONFIG_FILE = "llm_config.json"

# Initialize database on startup
init_db()

# Helper function to read LLM config
def get_llm_config() -> LLMConfig:
    try:
        with open(LLM_CONFIG_FILE, "r") as f:
            config_data = json.load(f)
            return LLMConfig(**config_data)
    except (FileNotFoundError, json.JSONDecodeError):
        # Default config if file not found or invalid
        default_provider = os.getenv("LLM_PROVIDER", "ollama")

        # Determine the model based on the provider
        if default_provider == "ollama":
            default_model = os.getenv("OLLAMA_MODEL", "llama3.2")
        elif default_provider == "openai":
            default_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        else:
            # Fallback for unknown provider name from env, try specific model envs, then generic default
            default_model = os.getenv(f"{default_provider.upper()}_MODEL") # e.g. ENV_OLLAMA_MODEL
            if not default_model:
                 # If provider-specific model env not found, try generic ones
                 default_model = os.getenv("OLLAMA_MODEL") or os.getenv("OPENAI_MODEL")
            if not default_model: # Absolute fallback if no model env var is useful
                 default_model = "default_model_please_configure"

        # This final check ensures that if a known provider was identified (ollama/openai)
        # but its specific model env var was empty, it still gets a sensible default.
        if not default_model: # Should ideally not be hit if logic above is sound
            if default_provider == "ollama":
                default_model = "llama3.2"
            elif default_provider == "openai":
                default_model = "gpt-4o-mini"
            else: # Should be caught by earlier specific assignment or "default_model_please_configure"
                default_model = "unknown_fallback_model"


        return LLMConfig(provider=default_provider, model=default_model)

# Helper function to write LLM config
def save_llm_config(config: LLMConfig):
    with open(LLM_CONFIG_FILE, "w") as f:
        json.dump(config.model_dump(), f, indent=2) # Changed from dict() to model_dump()

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

@app.get("/api/llm/health")
def check_llm_health(provider_name: Optional[str] = None):
    """Check the health of a specific LLM provider and list its models."""
    config = get_llm_config()
    # Use provided provider_name or fallback to current config, then default
    provider_to_check = provider_name or config.provider

    try:
        provider_instance = create_llm_provider(provider_type=provider_to_check)
        is_healthy = provider_instance.health_check()
        models = []
        if hasattr(provider_instance, 'list_models'):
            models = provider_instance.list_models()
        
        return {
            "provider": provider_to_check,
            "healthy": is_healthy,
            "models": models
        }
    except Exception as e:
        logger.error(f"LLM health check for {provider_to_check} failed: {str(e)}")
        return {
            "provider": provider_to_check,
            "healthy": False,
            "error": str(e),
            "models": []
        }


@app.get("/api/questions/ai", response_model=List[Question])
def generate_ai_questions(subject: str, limit: Optional[int] = 5):
    """Generate AI-powered questions for a specific subject using configured LLM provider"""
    config = get_llm_config()
    try:
        # Get default limit from environment if not provided
        if limit is None:
            limit = int(os.getenv("DEFAULT_QUESTION_LIMIT", "5"))
        
        provider = create_llm_provider(provider_type=config.provider, model=config.model)
        
        logger.info(f"Using {config.provider} model: {config.model} for AI questions")
        
        # Generate questions using the provider
        questions = provider.generate_questions(subject, limit)
        
        logger.info(f"Generated {len(questions)} AI questions for subject: {subject} using {config.provider} provider")
        return questions
        
    except Exception as e:
        logger.error(f"AI question generation failed: {str(e)}")
        error_msg = f"{config.provider.capitalize()} question generation failed: {str(e)}."
        
        if config.provider == "openai":
            error_msg += " Please check your OpenAI API key and quota."
        elif config.provider == "ollama":
            error_msg += " Please check if Ollama is running locally."
        
        raise HTTPException(status_code=503, detail=error_msg)

@app.get("/api/llm/config", response_model=LLMConfig)
def get_current_llm_config_endpoint():
    """Get the current LLM configuration."""
    return get_llm_config()

@app.post("/api/llm/config", response_model=LLMConfig)
async def set_llm_config_endpoint(new_config: LLMConfig):
    """Set the LLM configuration."""
    try:
        # Validate provider
        provider_instance = create_llm_provider(provider_type=new_config.provider, model=new_config.model)
        if not provider_instance.health_check():
            raise HTTPException(status_code=400, detail=f"Provider {new_config.provider} with model {new_config.model} is not healthy or available.")

        # Validate model for the provider (basic check if list_models is available)
        if hasattr(provider_instance, 'list_models'):
            available_models = provider_instance.list_models()
            if new_config.model not in available_models:
                # If model not in list, it could be a custom one for Ollama, so we only warn for now
                # For OpenAI, this would be a stricter check if we had a definitive list
                logger.warning(f"Model '{new_config.model}' not in reported available models for {new_config.provider}: {available_models}")

        save_llm_config(new_config)
        logger.info(f"LLM configuration updated: Provider={new_config.provider}, Model={new_config.model}")
        return new_config
    except ValueError as ve: # Handles unknown provider type from create_llm_provider
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Failed to set LLM configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to set LLM configuration: {str(e)}")


@app.get("/api/llm/providers")
def get_llm_providers_endpoint():
    """Get list of available LLM providers and their status."""
    # This function in llm_providers.py needs to be updated
    # to return more detailed info, including health and models for each.
    # For now, it just lists providers that are generally available.
    
    # Potential enhancement: get_available_providers could return a list of dicts
    # with {"name": "ollama", "healthy": True, "models": ["llama3.2", ...]}
    providers_info = []
    for p_name in ["ollama", "openai"]: # Check known providers
        try:
            p_instance = create_llm_provider(p_name)
            healthy = p_instance.health_check()
            models = []
            if hasattr(p_instance, 'list_models'):
                models = p_instance.list_models()
            providers_info.append({
                "name": p_name,
                "healthy": healthy,
                "models": models
            })
        except Exception: # If provider setup fails (e.g. missing keys)
            providers_info.append({
                "name": p_name,
                "healthy": False,
                "models": []
            })

    current_config = get_llm_config()
    return {
        "current_provider": current_config.provider,
        "current_model": current_config.model,
        "available_providers": providers_info
    }


@app.get("/api/models")
def get_models_endpoint(provider: str):
    """Get list of available models for a specific provider."""
    if not provider:
        raise HTTPException(status_code=400, detail="Provider query parameter is required.")
    try:
        provider_instance = create_llm_provider(provider_type=provider)
        if hasattr(provider_instance, 'list_models'):
            models = provider_instance.list_models()
            return {"provider": provider, "models": models}
        else:
            # Fallback or error if list_models is not implemented for the provider
            logger.warning(f"list_models not implemented for provider: {provider}")
            return {"provider": provider, "models": []} # Or raise HTTPException
    except ValueError as ve: # Handles unknown provider type
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Failed to get models for provider {provider}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not retrieve models for {provider}.")

if __name__ == "__main__":
    import uvicorn
    
    # Initialize database
    init_db()
    
    # Get host and port from environment
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    
    # Log initial LLM config from file or defaults
    initial_config = get_llm_config()
    logger.info(f"Starting Quizly API server with LLM provider: {initial_config.provider}, Model: {initial_config.model}")
    if initial_config.provider == "ollama":
        logger.info(f"Ollama host: {os.getenv('OLLAMA_HOST', 'http://localhost:11434')}")
    elif initial_config.provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            logger.warning("OPENAI_API_KEY is not set. OpenAI provider may not function.")

    # Start server
    uvicorn.run(app, host=host, port=port)