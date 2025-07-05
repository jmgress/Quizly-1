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
from logging_config_manager import LoggingConfigManager # New import

import logging
import logging.config # New import
import logging.handlers # New import for RotatingFileHandler

# Initialize logging configuration manager
# It will load from ../logging_config.json relative to this main.py file
logging_config_mgr = LoggingConfigManager(config_file=os.path.join(os.path.dirname(__file__), "..", "logging_config.json"))

# Global logger for main application scope, will be configured by setup_logging
logger = logging.getLogger("api_server") # Changed from __name__ to be component specific

# --- Logging Setup Function ---
def setup_logging():
    """Configures logging based on logging_config.json."""
    config = logging_config_mgr.get_config()
    log_dir_base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))

    if not os.path.exists(log_dir_base):
        os.makedirs(log_dir_base, exist_ok=True)

    log_level_map = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "TRACE": logging.DEBUG, # Python logging doesn't have TRACE, map to DEBUG
        "NOTSET": logging.NOTSET,
    }

    # Basic stream handler for console output
    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "level": log_level_map.get(config.get("global_level", "INFO").upper(), logging.INFO),
            "stream": "ext://sys.stdout",
        }
    }

    # Configure file handlers if enabled
    if config.get("enable_file_logging", False):
        log_files = config.get("log_files", {})
        rotation_max_bytes = config.get("log_rotation_max_bytes", 10*1024*1024)
        rotation_backup_count = config.get("log_rotation_backup_count", 5)

        for key, relative_path in log_files.items():
            # Ensure paths are absolute, relative to project root's "logs" directory
            log_file_path = os.path.join(log_dir_base, os.path.relpath(relative_path, "logs"))
            log_file_dir = os.path.dirname(log_file_path)
            os.makedirs(log_file_dir, exist_ok=True)

            handler_name = f"file_{key}"
            handlers[handler_name] = {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "verbose",
                "filename": log_file_path,
                "maxBytes": rotation_max_bytes,
                "backupCount": rotation_backup_count,
                "level": logging.DEBUG, # Handlers should capture all, loggers control level
            }

    # Define logger configurations
    # The root logger will use the global_level and console output by default
    # Specific loggers will inherit from root but can have their own levels.
    configured_loggers = {
        "root": {
            "handlers": ["console"] + ([f"file_{key}" for key in config.get("log_files", {}).keys() if config.get("enable_file_logging")] if "combined" in config.get("log_files", {}) else []),
            "level": log_level_map.get(config.get("global_level", "INFO").upper(), logging.INFO),
        },
        "api_server": { # Corresponds to logger = logging.getLogger("api_server")
            "handlers": ["console"] + ([f"file_backend_api", f"file_combined", f"file_backend_error"] if config.get("enable_file_logging") else []),
            "level": log_level_map.get(config.get("backend_levels", {}).get("api_server", "INFO").upper(), logging.INFO),
            "propagate": False, # Avoid duplicating to root if specific handlers are set
        },
        "llm_providers": {
            "handlers": ["console"] + ([f"file_backend_llm", f"file_combined", f"file_backend_error"] if config.get("enable_file_logging") else []),
            "level": log_level_map.get(config.get("backend_levels", {}).get("llm_providers", "INFO").upper(), logging.INFO),
            "propagate": False,
        },
        "database": {
            "handlers": ["console"] + ([f"file_backend_database", f"file_combined", f"file_backend_error"] if config.get("enable_file_logging") else []),
            "level": log_level_map.get(config.get("backend_levels", {}).get("database", "WARNING").upper(), logging.WARNING),
            "propagate": False,
        },
        # Add other specific loggers as needed, e.g., for third-party libraries
        "uvicorn.error": { # To capture uvicorn errors if needed
            "handlers": ["console"] + ([f"file_backend_error", f"file_combined"] if config.get("enable_file_logging") else []),
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
             "handlers": ["console"] + ([f"file_backend_api", f"file_combined"] if config.get("enable_file_logging") else []),
             "level": "INFO",
             "propagate": False,
        }
    }

    # Filter configuration for loggers: only include loggers that will write to specific files
    # if file logging is enabled. This ensures error.log gets only ERROR+ from relevant loggers.
    if config.get("enable_file_logging"):
        # Special handling for error log: ensure it gets only ERROR or CRITICAL
        if "file_backend_error" in handlers:
             handlers["file_backend_error"]["level"] = logging.ERROR # Override level for error file

        # Assign specific file handlers to loggers
        # Example: api_server logs go to backend_api.log, combined.log, and errors to backend_error.log
        # This logic is now embedded in the 'handlers' list for each logger above.
        # The 'combined.log' should get logs from all backend components.
        # We can achieve this by adding 'file_combined' to handlers of all backend loggers,
        # or by making the root logger write to 'file_combined' and ensuring backend loggers propagate to root.
        # For now, explicit handler assignment in each logger is clearer.

        # Ensure 'file_combined' handler is added to root if not explicitly handled by all sub-loggers
        if "file_combined" in handlers and "file_combined" not in configured_loggers["root"]["handlers"]:
            configured_loggers["root"]["handlers"].append("file_combined")

    # Apply the logging configuration
    logging_config_dict = {
        "version": 1,
        "disable_existing_loggers": False, # Important to not disable uvicorn/fastapi loggers
        "formatters": {
            "verbose": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"
            },
            "simple": {
                "format": "%(levelname)s - %(message)s"
            },
        },
        "handlers": handlers,
        "loggers": configured_loggers,
        # "root" logger config is implicitly handled by configuring "root" in "loggers"
    }

    logging.config.dictConfig(logging_config_dict)
    logger.info("Logging setup complete using dictConfig.")

# --- End Logging Setup ---

# Call setup_logging on application startup
setup_logging()

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


# --- Logging API Endpoints ---

@app.get("/api/logging/config")
def get_logging_config():
    """Get current logging configuration."""
    try:
        return logging_config_mgr.get_config()
    except Exception as e:
        logger.error(f"Error getting logging config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get logging configuration: {str(e)}")

@app.put("/api/logging/config")
def update_logging_config(config_update: dict):
    """Update logging configuration and re-apply."""
    try:
        # Basic validation for top-level keys
        valid_top_keys = [
            "global_level", "frontend_level", "backend_levels",
            "log_files", "log_rotation_max_bytes",
            "log_rotation_backup_count", "enable_file_logging"
        ]
        # Further validation can be added here, e.g., for log levels, path formats
        for key in config_update.keys():
            if key not in valid_top_keys:
                raise HTTPException(status_code=400, detail=f"Invalid logging configuration key: {key}")

        updated_config = logging_config_mgr.update_config(config_update)
        setup_logging() # Re-initialize logging with new config
        logger.info("Logging configuration updated and re-applied.")
        return {"message": "Logging configuration updated successfully", "config": updated_config}
    except HTTPException: # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error updating logging config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update logging configuration: {str(e)}")

@app.get("/api/logging/logs")
def get_log_entries(
    component: Optional[str] = None,
    level: Optional[str] = None,
    lines: Optional[int] = 100
):
    """Fetch log entries, optionally filtered by component and level."""
    config = logging_config_mgr.get_config()
    if not config.get("enable_file_logging"):
        return {"message": "File logging is not enabled.", "logs": []}

    log_files_map = config.get("log_files", {})
    target_log_file_key = None

    if component:
        # Map component to log file key in config (e.g., "backend_api" -> "backend_api")
        # This assumes component name matches the key in log_files or a predefined mapping
        if component == "frontend": target_log_file_key = "frontend_app"
        elif component == "api": target_log_file_key = "backend_api"
        elif component == "llm": target_log_file_key = "backend_llm"
        elif component == "database": target_log_file_key = "backend_database"
        elif component == "error": target_log_file_key = "backend_error"
        elif component == "combined": target_log_file_key = "combined"
        else: # Allow direct key if component name matches a log_files key
            if component in log_files_map:
                target_log_file_key = component
            else:
                raise HTTPException(status_code=400, detail=f"Invalid log component: {component}")
    else: # Default to combined log if no component specified
        target_log_file_key = "combined"

    if not target_log_file_key or target_log_file_key not in log_files_map:
        raise HTTPException(status_code=404, detail=f"Log file for component '{component}' not found in configuration.")

    log_file_relative_path = log_files_map[target_log_file_key]
    # Ensure path is relative to project root's "logs" directory for reading
    log_dir_base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
    log_file_path = os.path.join(log_dir_base, os.path.relpath(log_file_relative_path, "logs"))


    if not os.path.exists(log_file_path):
        return {"message": f"Log file {log_file_path} not found.", "logs": []}

    try:
        entries = []
        with open(log_file_path, 'r') as f:
            # Read last N lines (more efficient ways exist for large files, but this is simplest)
            all_lines = f.readlines()
            selected_lines = all_lines[-lines:] if lines > 0 else all_lines

        for line in selected_lines:
            if level:
                # Simple string matching for level; more robust parsing could be added
                if f" - {level.upper()} - " in line:
                    entries.append(line.strip())
            else:
                entries.append(line.strip())
        return {"logs": entries, "file": log_file_path, "count": len(entries)}
    except Exception as e:
        logger.error(f"Error reading log file {log_file_path}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to read log file: {str(e)}")


from fastapi.responses import FileResponse

@app.get("/api/logging/actions/download/{log_key}")
async def download_log_file(log_key: str):
    """Download a specific log file."""
    config = logging_config_mgr.get_config()
    if not config.get("enable_file_logging"):
        raise HTTPException(status_code=400, detail="File logging is not enabled.")

    log_files_map = config.get("log_files", {})
    if log_key not in log_files_map:
        raise HTTPException(status_code=404, detail=f"Log key '{log_key}' not found in configuration.")

    log_file_relative_path = log_files_map[log_key]
    log_dir_base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
    log_file_path = os.path.join(log_dir_base, os.path.relpath(log_file_relative_path, "logs"))

    if not os.path.exists(log_file_path):
        raise HTTPException(status_code=404, detail=f"Log file {log_file_path} not found.")

    return FileResponse(log_file_path, media_type='text/plain', filename=os.path.basename(log_file_path))

@app.post("/api/logging/actions/clear/{log_key}")
async def clear_log_file(log_key: str):
    """Clear a specific log file."""
    config = logging_config_mgr.get_config()
    if not config.get("enable_file_logging"):
        raise HTTPException(status_code=400, detail="File logging is not enabled.")

    log_files_map = config.get("log_files", {})
    if log_key not in log_files_map:
        raise HTTPException(status_code=404, detail=f"Log key '{log_key}' not found in configuration.")

    log_file_relative_path = log_files_map[log_key]
    log_dir_base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
    log_file_path = os.path.join(log_dir_base, os.path.relpath(log_file_relative_path, "logs"))

    if not os.path.exists(log_file_path):
        raise HTTPException(status_code=404, detail=f"Log file {log_file_path} not found.")

    try:
        with open(log_file_path, 'w') as f: # Open in write mode to truncate
            f.write("")
        logger.info(f"Log file {log_file_path} cleared by user.")
        return {"message": f"Log file {log_key} ({os.path.basename(log_file_path)}) cleared successfully."}
    except Exception as e:
        logger.error(f"Error clearing log file {log_file_path}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear log file: {str(e)}")


@app.post("/api/logging/actions/rotate/{log_key}")
async def rotate_log_file(log_key: str):
    """Manually trigger log rotation for a specific log file."""
    # This requires finding the specific handler and calling doRollover.
    # This is more complex as it needs access to the configured handlers.
    # For simplicity, we might need to re-think or simplify this.
    # One approach: re-setup logging, which might trigger rotation if conditions are met,
    # or find the handler in logging.getLogger().handlers.

    # Find the handler associated with log_key
    # This is a simplified conceptual implementation. A more robust one would inspect logging.config.

    config = logging_config_mgr.get_config()
    if not config.get("enable_file_logging", False):
        raise HTTPException(status_code=400, detail="File logging is not enabled.")

    log_files_map = config.get("log_files", {})
    if log_key not in log_files_map:
        raise HTTPException(status_code=404, detail=f"Log key '{log_key}' not found in configuration.")

    # The actual file path
    log_file_relative_path = log_files_map[log_key]
    log_dir_base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
    target_log_filename = os.path.join(log_dir_base, os.path.relpath(log_file_relative_path, "logs"))

    # Iterate through all loggers and their handlers to find the one for the target file
    found_handler = False
    for logger_name in logging.Logger.manager.loggerDict:
        current_logger = logging.getLogger(logger_name)
        if hasattr(current_logger, 'handlers'):
            for handler in current_logger.handlers:
                if isinstance(handler, logging.handlers.RotatingFileHandler):
                    if hasattr(handler, 'baseFilename') and handler.baseFilename == target_log_filename:
                        handler.doRollover()
                        found_handler = True
                        logger.info(f"Manual log rotation triggered for {target_log_filename} via logger {logger_name}")
                        break
            if found_handler:
                break

    # Also check root handlers
    if not found_handler:
        for handler in logging.root.handlers:
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                if hasattr(handler, 'baseFilename') and handler.baseFilename == target_log_filename:
                    handler.doRollover()
                    found_handler = True
                    logger.info(f"Manual log rotation triggered for {target_log_filename} via root logger")
                    break

    if found_handler:
        return {"message": f"Log rotation triggered for {log_key} ({os.path.basename(target_log_filename)})."}
    else:
        logger.warning(f"Could not find a RotatingFileHandler for log key {log_key} (file: {target_log_filename}) to manually rotate.")
        raise HTTPException(status_code=404, detail=f"No active rotating file handler found for log key {log_key}. Rotation might happen automatically based on size.")

# --- End Logging API Endpoints ---


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
    
    # Start server
    uvicorn.run(app, host=host, port=port)