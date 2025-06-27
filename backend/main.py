from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import json
import uuid
from datetime import datetime
import ollama
import time # For request timing

# Import the logger
from logger import app_logger # Assuming logger.py is in the same directory or accessible via PYTHONPATH

app = FastAPI(title="Quizly API", description="Knowledge Testing Application API")

# Logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    app_logger.info(f"Incoming request: {request.method} {request.url.path}")
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    app_logger.info(f"Request finished: {request.method} {request.url.path} - Status: {response.status_code} - Took: {process_time:.2f}ms")
    return response

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
    app_logger.info("Initializing database...")
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
        app_logger.info("No questions found in DB, inserting sample questions.")
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
    app_logger.info("Database initialization complete.")

# Initialize database on startup
init_db()

@app.get("/")
def read_root():
    app_logger.info("Root endpoint accessed.")
    return {"message": "Welcome to Quizly API"}

@app.get("/api/questions", response_model=List[Question])
def get_questions(category: Optional[str] = None, limit: Optional[int] = 10):
    """Get quiz questions, optionally filtered by category"""
    app_logger.debug(f"Fetching questions. Category: {category}, Limit: {limit}")
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    
    query = "SELECT * FROM questions"
    params = []

    if category:
        query += " WHERE category = ?"
        params.append(category)

    if limit and limit <= 1000: # Standard limit for user quizzes
        query += " ORDER BY RANDOM() LIMIT ?"
        params.append(limit)
    elif limit and limit > 1000: # Admin fetching all questions
        query += " ORDER BY id"
        # No additional params needed for this case if category is None
    else: # Default case if no limit or invalid limit for non-admin
        query += " ORDER BY RANDOM() LIMIT ?"
        params.append(10) # Default limit

    app_logger.debug(f"Executing query: {query} with params: {params}")
    cursor.execute(query, tuple(params))
    
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
    app_logger.info(f"Retrieved {len(questions)} questions. Category: {category}, Limit: {limit}")
    return questions

@app.post("/api/quiz/submit", response_model=QuizResult)
def submit_quiz(submission: QuizSubmission):
    """Submit quiz answers and get results"""
    app_logger.info(f"Quiz submission received with {len(submission.answers)} answers.")
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    
    # Get correct answers for submitted questions
    question_ids = [answer.question_id for answer in submission.answers]
    placeholders = ','.join(['?'] * len(question_ids)) if question_ids else ''
    db_correct_answers = {}
    if placeholders:
        app_logger.debug(f"Fetching correct answers for question IDs: {question_ids}")
        cursor.execute(
            f"SELECT id, correct_answer FROM questions WHERE id IN ({placeholders})",
            question_ids
        )
        db_correct_answers = {row[0]: row[1] for row in cursor.fetchall()}
        app_logger.debug(f"Found {len(db_correct_answers)} correct answers from DB.")
    else:
        app_logger.warning("No question IDs provided in submission to fetch correct answers.")
    
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
    
    app_logger.info(f"Quiz session {quiz_id} saved. Score: {correct_count}/{total_questions} ({score_percentage:.2f}%).")

    result = QuizResult(
        quiz_id=quiz_id,
        total_questions=total_questions,
        correct_answers=correct_count,
        score_percentage=score_percentage,
        answers=answer_details
    )
    app_logger.debug(f"Returning quiz result: {result}")
    return result

@app.get("/api/quiz/{quiz_id}", response_model=QuizResult)
def get_quiz_result(quiz_id: str):
    """Get quiz results by ID"""
    app_logger.info(f"Fetching quiz result for quiz_id: {quiz_id}")
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM quiz_sessions WHERE id = ?", (quiz_id,))
    row = cursor.fetchone()
    
    if not row:
        app_logger.warning(f"Quiz session not found for quiz_id: {quiz_id}")
        raise HTTPException(status_code=404, detail="Quiz session not found")
    
    conn.close()
    app_logger.info(f"Quiz session found for quiz_id: {quiz_id}")
    
    result = QuizResult(
        quiz_id=row[0],
        total_questions=row[1],
        correct_answers=row[2],
        score_percentage=row[3],
        answers=json.loads(row[5])
    )
    app_logger.debug(f"Returning quiz result for {quiz_id}: {result}")
    return result

@app.put("/api/questions/{question_id}", response_model=Question)
def update_question(question_id: int, question_update: QuestionUpdate):
    """Update a question's fields"""
    app_logger.info(f"Updating question_id: {question_id} with data: {question_update.model_dump_json(exclude_none=True)}")
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    
    # First, check if the question exists
    cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        app_logger.warning(f"Update failed: Question not found for question_id: {question_id}")
        raise HTTPException(status_code=404, detail="Question not found")
    
    app_logger.debug(f"Question {question_id} found, proceeding with update.")
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
            app_logger.error(f"Validation error for question {question_id}: Must have 4 options.")
            raise HTTPException(status_code=400, detail="Question must have exactly 4 options")
        option_ids = [opt.id for opt in question_update.options]
        if len(set(option_ids)) != 4 or not all(id in ['a', 'b', 'c', 'd'] for id in option_ids):
            app_logger.error(f"Validation error for question {question_id}: Option ID issue.")
            raise HTTPException(status_code=400, detail="Options must have unique IDs 'a', 'b', 'c', 'd'")
        update_data["options"] = json.dumps([{"id": opt.id, "text": opt.text} for opt in question_update.options])
    if question_update.correct_answer is not None:
        # Validate correct answer
        if question_update.options: # if options are also being updated, use those
            valid_ids = [opt.id for opt in question_update.options]
        else: # otherwise, use current options from DB
            valid_ids = [opt["id"] for opt in current_question["options"]]
        if question_update.correct_answer not in valid_ids:
            app_logger.error(f"Validation error for question {question_id}: Invalid correct_answer.")
            raise HTTPException(status_code=400, detail="Correct answer must be one of the option IDs")
        update_data["correct_answer"] = question_update.correct_answer
    if question_update.category is not None:
        update_data["category"] = question_update.category
    
    # Build dynamic UPDATE query
    if update_data:
        app_logger.debug(f"Update data for question {question_id}: {update_data.keys()}")
        set_clause = ", ".join([f"{key} = ?" for key in update_data.keys()])
        query = f"UPDATE questions SET {set_clause} WHERE id = ?"
        values = list(update_data.values()) + [question_id]
        cursor.execute(query, values)
        conn.commit()
        app_logger.info(f"Question {question_id} updated successfully.")
    else:
        app_logger.info(f"No update data provided for question {question_id}. No changes made.")
    
    # Return updated question
    cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
    row = cursor.fetchone() # Should not be None as we checked earlier
    conn.close()
    
    updated_q = {
        "id": row[0],
        "text": row[1],
        "options": json.loads(row[2]),
        "correct_answer": row[3],
        "category": row[4]
    }
    app_logger.debug(f"Returning updated question {question_id}: {updated_q}")
    return updated_q

@app.get("/api/categories")
def get_categories():
    """Get available quiz categories"""
    app_logger.info("Fetching all distinct categories.")
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT category FROM questions")
    categories = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    app_logger.info(f"Found {len(categories)} distinct categories.")
    return {"categories": categories}

@app.get("/api/questions/ai", response_model=List[Question])
def generate_ai_questions(subject: str, limit: Optional[int] = 5):
    """Generate AI-powered questions for a specific subject using Ollama"""
    app_logger.info(f"AI question generation request. Subject: {subject}, Limit: {limit}")
    try:
        # Create a prompt for generating quiz questions
        prompt = f"""Generate {limit} multiple-choice quiz questions about {subject}. 
        Each question should have exactly 4 answer options labeled a, b, c, d.
        Format your response as a JSON array where each question has this structure:
        {{
            "text": "question text here?",
            "options": [
                {{"id": "a", "text": "option A text"}},
                {{"id": "b", "text": "option B text"}},
                {{"id": "c", "text": "option C text"}},
                {{"id": "d", "text": "option D text"}}
            ],
            "correct_answer": "a",
            "category": "{subject.lower()}"
        }}
        
        Return only the JSON array, no additional text."""

        app_logger.debug(f"Prompt for Ollama: {prompt[:200]}...") # Log a snippet of the prompt
        # Call Ollama to generate questions
        response = ollama.chat(
            model='llama3.2',  # Using a common model, can be configurable
            messages=[{
                'role': 'user', 
                'content': prompt
            }]
        )
        app_logger.debug(f"Ollama response received. Content snippet: {response['message']['content'][:200]}...")
        
        # Parse the response
        parsed_questions = []
        try:
            content_str = response['message']['content']
            # Try to find JSON array/object within the content string if it's not pure JSON
            json_start = content_str.find('[')
            json_end = content_str.rfind(']') + 1
            if json_start == -1 or json_end == 0 : # If no array, try for object
                json_start = content_str.find('{')
                json_end = content_str.rfind('}') + 1

            if json_start != -1 and json_end != 0 and json_end > json_start:
                json_str = content_str[json_start:json_end]
                app_logger.debug(f"Extracted JSON string: {json_str[:200]}...")
                questions_data = json.loads(json_str)
            else:
                app_logger.warning("No JSON array/object found in Ollama response, attempting direct parse.")
                questions_data = json.loads(content_str) # Direct parse attempt
            
            # Ensure we have a list
            if not isinstance(questions_data, list):
                questions_data = [questions_data] # Wrap single object in a list
            
            # Convert to our format and add IDs
            for i, q_data in enumerate(questions_data[:limit]):
                # Validate the structure
                if not all(key in q_data for key in ['text', 'options', 'correct_answer']):
                    app_logger.warning(f"Skipping AI question due to missing keys: {q_data}")
                    continue

                # Further validation for options format
                if not isinstance(q_data['options'], list) or len(q_data['options']) != 4:
                    app_logger.warning(f"Skipping AI question due to invalid options format: {q_data}")
                    continue
                if not all('id' in opt and 'text' in opt for opt in q_data['options']):
                    app_logger.warning(f"Skipping AI question due to malformed options: {q_data}")
                    continue

                parsed_questions.append({
                    "id": 1000 + i,  # Use high IDs to avoid conflicts with DB questions
                    "text": q_data["text"],
                    "options": q_data["options"],
                    "correct_answer": q_data["correct_answer"],
                    "category": subject.lower()
                })
            
            if not parsed_questions:
                app_logger.error("No valid questions generated by AI after parsing.")
                raise ValueError("No valid questions generated by AI.")
            
            app_logger.info(f"Successfully generated {len(parsed_questions)} AI questions for subject: {subject}")
            return parsed_questions

        except json.JSONDecodeError as je:
            app_logger.error(f"JSONDecodeError while parsing AI response: {je}. Response content: {response['message']['content']}")
            raise ValueError(f"Could not parse AI response: {je}")
        except Exception as ex: # Catch other parsing/validation errors
            app_logger.error(f"Error processing AI response: {ex}. Response content: {response['message']['content']}")
            raise ValueError(f"Error processing AI response: {ex}")

    except ollama.ResponseError as ore:
        app_logger.error(f"Ollama API ResponseError: {ore.status_code} - {ore.error}")
        detail_msg = f"AI question generation failed (Ollama ResponseError {ore.status_code}): {ore.error}. Ensure Ollama is running and model 'llama3.2' is available."
        if ore.status_code == 404: # Model not found
             detail_msg = f"AI question generation failed: Model 'llama3.2' not found on Ollama server. Please pull the model first (e.g., 'ollama pull llama3.2')."
        raise HTTPException(status_code=503, detail=detail_msg)
    except Exception as e:
        app_logger.error(f"AI question generation failed: {str(e)}")
        # If Ollama fails, return a fallback error
        raise HTTPException(
            status_code=503, 
            detail=f"AI question generation failed: {str(e)}. Please ensure Ollama is running and the llama3.2 model is available."
        )

if __name__ == "__main__":
    import uvicorn
    app_logger.info("Starting Quizly API with Uvicorn...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None) # Disable uvicorn's default logging to avoid duplicate messages with our custom logger
    app_logger.info("Quizly API has shut down.")

# Log retrieval endpoint
LOG_FILE_PATH = "quizly.log" # Make sure this matches the one in logger.py

class LogEntry(BaseModel):
    timestamp: str
    logger_name: str
    level: str
    module: str
    line: int
    message: str

@app.get("/api/logs", response_model=List[LogEntry])
def get_logs(
    level: Optional[str] = None,
    module_filter: Optional[str] = None, # Renamed from 'module' to avoid conflict
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0
):
    app_logger.info(f"Log retrieval request. Filters: level={level}, module={module_filter}, start={start_time}, end={end_time}, limit={limit}, offset={offset}")
    try:
        # Check if log file exists to prevent error on first run if no logs yet
        import os
        if not os.path.exists(LOG_FILE_PATH):
            app_logger.info(f"Log file {LOG_FILE_PATH} does not exist yet. Returning empty list.")
            return []

        with open(LOG_FILE_PATH, "r", encoding='utf-8') as f: # Added encoding
            log_lines = f.readlines()
    except FileNotFoundError: # Should be caught by os.path.exists, but as a safeguard
        app_logger.error(f"Log file not found at {LOG_FILE_PATH}")
        return []
    except Exception as e:
        app_logger.error(f"Error reading log file {LOG_FILE_PATH}: {e}")
        raise HTTPException(status_code=500, detail="Could not read log file.")

    log_entries = []
    # Log format from logger.py: "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"
    # Example: 2024-03-15 10:35:12,123 - quizly - INFO - main:42 - This is a log message.
    log_pattern = re.compile(
        r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - "
        r"(?P<logger_name>[\w.-]+) - "
        r"(?P<level>DEBUG|INFO|WARNING|ERROR|CRITICAL) - "
        r"(?P<module>[\w.-]+):(?P<line>\d+) - "
        r"(?P<message>.*)$"
    )
    import re # Ensure re is imported if not already at the top

    for line_content in reversed(log_lines): # Show newest logs first
        line_content = line_content.strip()
        if not line_content: # Skip empty lines
            continue
        match = log_pattern.match(line_content)
        if match:
            entry_data = match.groupdict()

            # Filtering
            if level and entry_data['level'] != level.upper():
                continue
            if module_filter and not (module_filter.lower() in entry_data['module'].lower() or module_filter.lower() in entry_data['logger_name'].lower()):
                continue # Check against both module and logger name

            try:
                # Ensure timezone awareness if start_time/end_time are timezone-aware
                # For simplicity, assuming naive datetimes from query and log file
                log_timestamp = datetime.strptime(entry_data['timestamp'], "%Y-%m-%d %H:%M:%S,%f")
                if start_time and log_timestamp < start_time:
                    continue
                if end_time and log_timestamp > end_time:
                    # If we are going backwards and passed end_time, future older logs will also be passed
                    # This optimization works because logs are read in reverse chronological order
                    pass # No, this is not correct. We need to check all.
                         # If we are filtering for a specific day, logs from previous day (older) should still be processed.
            except ValueError as ve:
                app_logger.warning(f"Could not parse timestamp '{entry_data['timestamp']}' from log line: '{line_content}'. Error: {ve}")
                continue # Skip lines with unparseable timestamps

            log_entries.append(LogEntry(
                timestamp=entry_data['timestamp'],
                logger_name=entry_data['logger_name'],
                level=entry_data['level'],
                module=entry_data['module'],
                line=int(entry_data['line']),
                message=entry_data['message']
            ))

    # Apply pagination after all filters
    paginated_entries = log_entries[offset : offset + limit] # Slicing already handles list boundaries gracefully
    app_logger.info(f"Returning {len(paginated_entries)} of {len(log_entries)} matched log entries after filtering and pagination.")
    return paginated_entries