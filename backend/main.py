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

# Import configuration manager
from config_manager import config_manager

# Import logging configuration manager
from logging_config import logging_config_manager

import logging
import logging.handlers
import sys

# Initialize logging configuration manager
logging_config = logging_config_manager.get_config()

# Set up proper logging with file handlers
def setup_logging():
    """Set up logging with both console and file handlers"""
    
    # Create logs directory if it doesn't exist
    log_dir = logging_config.get('file_settings', {}).get('log_directory', 'logs')
    backend_log_dir = os.path.join(log_dir, 'backend')
    os.makedirs(backend_log_dir, exist_ok=True)
    
    # Get log format from config
    log_format = logging_config.get('file_settings', {}).get('log_format', 
                                                             '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handlers for different log types
    handlers = [
        ('api.log', logging.INFO),
        ('error.log', logging.ERROR),
        ('database.log', logging.DEBUG)
    ]
    
    for filename, level in handlers:
        filepath = os.path.join(backend_log_dir, filename)
        file_handler = logging.handlers.RotatingFileHandler(
            filepath, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    return root_logger

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Quizly API", description="Knowledge Testing Application API")

# Log application startup
logger.info("Initializing Quizly FastAPI application")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # React dev server and demo server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("CORS middleware configured for localhost:3000")

# Startup event handler
@app.on_event("startup")
async def startup_event():
    logger.info("=== Quizly API Server Starting ===")
    logger.info(f"FastAPI version: {app.version}")
    logger.info("Server is ready to accept requests")

# Shutdown event handler
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("=== Quizly API Server Shutting Down ===")
    logger.info("Server shutdown complete")

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

# Initialize database on startup
logger.info("Initializing database...")
init_db()
logger.info("Database initialization completed")

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to Quizly API"}

@app.get("/api/health")
def health_check():
    """Health check endpoint with logging"""
    logger.info("Health check endpoint accessed")
    logger.debug("Performing health check...")
    
    # Test logging at different levels
    logger.debug("Debug: Health check details")
    logger.info("Info: Health check successful")
    logger.warning("Warning: This is a test warning")
    
    return {
        "status": "healthy",
        "message": "Quizly API is running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/questions", response_model=List[Question])
def get_questions(category: Optional[str] = None, limit: Optional[int] = 10):
    """Get quiz questions, optionally filtered by category"""
    logger.info(f"Getting questions - category: {category}, limit: {limit}")
    
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    
    if category:
        cursor.execute("SELECT * FROM questions WHERE category = ? ORDER BY RANDOM() LIMIT ?", (category, limit))
        logger.info(f"Fetching {limit} questions from category: {category}")
    else:
        # For admin interface, allow fetching all questions by setting a high limit
        if limit and limit > 1000:
            cursor.execute("SELECT * FROM questions ORDER BY id")
            logger.info("Fetching all questions for admin interface")
        else:
            cursor.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT ?", (limit,))
            logger.info(f"Fetching {limit} random questions")
    
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
    logger.info(f"Returning {len(questions)} questions")
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
def check_llm_health():
    """Check the health of the configured LLM provider"""
    try:
        config = config_manager.get_config()
        provider = create_llm_provider()
        is_healthy = provider.health_check()
        provider_type = config["llm_provider"]
        
        return {
            "provider": provider_type,
            "healthy": is_healthy,
            "available_providers": get_available_providers()
        }
    except Exception as e:
        logger.error(f"LLM health check failed: {str(e)}")
        config = config_manager.get_config()
        return {
            "provider": config["llm_provider"],
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
        
        # Use provider from config manager or query parameter
        config = config_manager.get_config()
        provider_type = provider_type or config["llm_provider"]
        
        # Ensure model is properly set based on provider type
        if provider_type == "openai":
            used_model = model or config["openai_model"]
        else:
            used_model = model or config["ollama_model"]
        
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
    config = config_manager.get_config()
    current_provider = config["llm_provider"]
    
    return {
        "current": current_provider,
        "available": providers
    }


@app.get("/api/models")
def get_models(provider: Optional[str] = None):
    """Get list of available models for a provider"""
    provider_type = provider or config_manager.get_config()["llm_provider"]
    from llm_providers import get_available_models

    models = get_available_models(provider_type)
    return {"provider": provider_type, "models": models}

@app.get("/api/llm/config")
def get_llm_config():
    """Get current LLM configuration"""
    try:
        config = config_manager.get_config()
        provider_config = config_manager.get_provider_config()
        
        # Don't expose API key in response
        safe_config = config.copy()
        if "openai_api_key" in safe_config:
            safe_config["openai_api_key"] = "***" if safe_config["openai_api_key"] else ""
        
        return {
            "config": safe_config,
            "current_provider": provider_config
        }
    except Exception as e:
        logger.error(f"Error getting LLM config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get configuration: {str(e)}")

@app.put("/api/llm/config")
def update_llm_config(config_update: dict):
    """Update LLM configuration"""
    try:
        # Validate the configuration
        valid_keys = ["llm_provider", "ollama_model", "ollama_host", "openai_api_key", "openai_model"]
        invalid_keys = [key for key in config_update.keys() if key not in valid_keys]
        if invalid_keys:
            raise HTTPException(status_code=400, detail=f"Invalid configuration keys: {invalid_keys}")
        
        # Validate provider
        if "llm_provider" in config_update:
            if config_update["llm_provider"] not in ["ollama", "openai"]:
                raise HTTPException(status_code=400, detail="Provider must be 'ollama' or 'openai'")
        
        # Update configuration
        updated_config = config_manager.update_config(config_update)
        
        # Test the new configuration
        try:
            provider_config = config_manager.get_provider_config()
            if provider_config["provider"] == "ollama":
                provider = create_llm_provider("ollama", 
                                             model=provider_config["model"],
                                             host=provider_config["host"])
            else:
                provider = create_llm_provider("openai",
                                             model=provider_config["model"],
                                             api_key=provider_config["api_key"])
            
            # Test health check
            if not provider.health_check():
                logger.warning("Provider health check failed for new configuration")
                # Don't fail here, as the provider might be temporarily unavailable
            
        except Exception as e:
            logger.error(f"Error testing new configuration: {str(e)}")
            # Don't fail the update, just log the error
        
        # Return safe config (without API key)
        safe_config = updated_config.copy()
        if "openai_api_key" in safe_config:
            safe_config["openai_api_key"] = "***" if safe_config["openai_api_key"] else ""
        
        return {"config": safe_config, "message": "Configuration updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating LLM config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")

@app.get("/api/llm/providers/health")
def get_providers_health():
    """Get health status of all available providers"""
    providers_health = {}
    
    # Check Ollama
    try:
        config = config_manager.get_config()
        provider = create_llm_provider("ollama", 
                                     model=config["ollama_model"],
                                     host=config["ollama_host"])
        providers_health["ollama"] = {
            "healthy": provider.health_check(),
            "model": config["ollama_model"],
            "host": config["ollama_host"]
        }
    except Exception as e:
        providers_health["ollama"] = {
            "healthy": False,
            "error": str(e),
            "model": config_manager.get_config()["ollama_model"],
            "host": config_manager.get_config()["ollama_host"]
        }
    
    # Check OpenAI
    try:
        config = config_manager.get_config()
        if config["openai_api_key"]:
            provider = create_llm_provider("openai",
                                         model=config["openai_model"],
                                         api_key=config["openai_api_key"])
            providers_health["openai"] = {
                "healthy": provider.health_check(),
                "model": config["openai_model"],
                "api_key_set": bool(config["openai_api_key"])
            }
        else:
            providers_health["openai"] = {
                "healthy": False,
                "error": "API key not configured",
                "model": config["openai_model"],
                "api_key_set": False
            }
    except Exception as e:
        providers_health["openai"] = {
            "healthy": False,
            "error": str(e),
            "model": config_manager.get_config()["openai_model"],
            "api_key_set": bool(config_manager.get_config()["openai_api_key"])
        }
    
    return providers_health


# Logging Configuration Endpoints

@app.get("/api/logging/config")
def get_logging_config():
    """Get current logging configuration"""
    try:
        config = logging_config_manager.get_config()
        return {
            "config": config,
            "available_levels": ["ERROR", "WARN", "INFO", "DEBUG", "TRACE"]
        }
    except Exception as e:
        logger.error(f"Error getting logging config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get logging configuration: {str(e)}")


@app.put("/api/logging/config")
def update_logging_config(config_update: dict):
    """Update logging configuration"""
    try:
        # Validate log levels
        valid_levels = ["ERROR", "WARN", "INFO", "DEBUG", "TRACE"]
        
        if "log_levels" in config_update:
            for component, levels in config_update["log_levels"].items():
                if isinstance(levels, dict):
                    for subcomponent, level in levels.items():
                        if level not in valid_levels:
                            raise HTTPException(status_code=400, detail=f"Invalid log level: {level}")
                elif isinstance(levels, str):
                    if levels not in valid_levels:
                        raise HTTPException(status_code=400, detail=f"Invalid log level: {levels}")
        
        # Validate LLM prompt logging configuration
        if "llm_prompt_logging" in config_update:
            llm_config = config_update["llm_prompt_logging"]
            if "level" in llm_config and llm_config["level"] not in valid_levels:
                raise HTTPException(status_code=400, detail=f"Invalid LLM prompt logging level: {llm_config['level']}")
            if "enabled" in llm_config and not isinstance(llm_config["enabled"], bool):
                raise HTTPException(status_code=400, detail="LLM prompt logging enabled must be a boolean")
        
        # Update configuration
        updated_config = logging_config_manager.update_config(config_update)
        
        return {
            "success": True,
            "config": updated_config
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating logging config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update logging configuration: {str(e)}")


@app.get("/api/logging/files")
def get_log_files():
    """Get list of available log files"""
    try:
        files = logging_config_manager.get_log_files()
        return {"files": files}
    except Exception as e:
        logger.error(f"Error getting log files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get log files: {str(e)}")


@app.get("/api/logging/recent")
def get_recent_logs(max_entries: int = 100):
    """Get recent log entries"""
    try:
        logs = logging_config_manager.get_recent_logs(max_entries)
        return {"logs": logs}
    except Exception as e:
        logger.error(f"Error getting recent logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get recent logs: {str(e)}")


@app.get("/api/logging/llm-prompts")
def get_llm_prompt_logs(max_entries: int = 100):
    """Get recent LLM prompt logs"""
    try:
        logs = logging_config_manager.get_llm_prompt_logs(max_entries)
        return {"logs": logs}
    except Exception as e:
        logger.error(f"Error getting LLM prompt logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get LLM prompt logs: {str(e)}")


@app.post("/api/logging/llm-prompts/clear")
def clear_llm_prompt_logs():
    """Clear LLM prompt logs"""
    try:
        log_file = logging_config_manager.get_llm_prompt_log_file()
        logging_config_manager.clear_log_file(log_file)
        return {"message": "LLM prompt logs cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing LLM prompt logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear LLM prompt logs: {str(e)}")


@app.get("/api/logging/llm-prompts/download")
def download_llm_prompt_logs():
    """Download LLM prompt logs"""
    try:
        log_file = logging_config_manager.get_llm_prompt_log_file()
        return download_log_file(log_file)
    except Exception as e:
        logger.error(f"Error downloading LLM prompt logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to download LLM prompt logs: {str(e)}")


@app.post("/api/logging/files/{file_path:path}/clear")
def clear_log_file(file_path: str):
    """Clear a specific log file"""
    try:
        logging_config_manager.clear_log_file(file_path)
        return {"success": True, "message": f"Log file {file_path} cleared successfully"}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error clearing log file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear log file: {str(e)}")


@app.post("/api/logging/files/{file_path:path}/rotate")
def rotate_log_file(file_path: str):
    """Rotate a specific log file"""
    try:
        logging_config_manager.rotate_log_file(file_path)
        return {"success": True, "message": f"Log file {file_path} rotated successfully"}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error rotating log file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to rotate log file: {str(e)}")


@app.get("/api/logging/files/{file_path:path}/download")
def download_log_file(file_path: str):
    """Download a specific log file"""
    try:
        from fastapi.responses import FileResponse
        import os
        
        # Validate path to prevent directory traversal
        full_path = logging_config_manager._validate_safe_path(file_path)
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="Log file not found")
        
        return FileResponse(
            path=full_path,
            filename=os.path.basename(file_path),
            media_type="text/plain"
        )
    except ValueError as e:
        logger.error(f"Invalid file path {file_path}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid file path: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading log file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to download log file: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    # Initialize database
    init_db()
    
    # Get host and port from environment
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    
    # Log provider configuration
    config = config_manager.get_config()
    provider_type = config["llm_provider"]
    logger.info(f"Starting Quizly API server with LLM provider: {provider_type}")
    
    if provider_type == "openai":
        logger.info(f"OpenAI model: {config['openai_model']}")
        logger.info(f"OpenAI API key configured: {bool(config['openai_api_key'])}")
    elif provider_type == "ollama":
        logger.info(f"Ollama model: {config['ollama_model']}")
        logger.info(f"Ollama host: {config['ollama_host']}")
    
    # Start server with proper logging
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        log_level="info",
        access_log=True,
        loop="asyncio"
    )