from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import json
import uuid
from datetime import datetime
import ollama
from logger import info, debug, warning, error, get_logs

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

class LogConfig(BaseModel):
    level: str

# Database initialization
def init_db():
    info("Initializing database", "database")
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
    debug("Questions table created/verified", "database")
    
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
    debug("Quiz sessions table created/verified", "database")
    
    # Insert sample questions if table is empty
    cursor.execute("SELECT COUNT(*) FROM questions")
    question_count = cursor.fetchone()[0]
    if question_count == 0:
        info("No questions found, inserting sample questions", "database")
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
        info(f"Inserted {len(sample_questions)} sample questions", "database")
    else:
        info(f"Found {question_count} existing questions", "database")
    
    conn.commit()
    conn.close()
    info("Database initialization completed", "database")

# Initialize database on startup
info("Starting Quizly API", "startup")
init_db()

@app.get("/")
def read_root():
    info("Root endpoint accessed", "api")
    return {"message": "Welcome to Quizly API"}

@app.get("/api/questions", response_model=List[Question])
def get_questions(category: Optional[str] = None, limit: Optional[int] = 10):
    """Get quiz questions, optionally filtered by category"""
    info(f"Fetching questions: category={category}, limit={limit}", "api")
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    
    if category:
        cursor.execute("SELECT * FROM questions WHERE category = ? ORDER BY RANDOM() LIMIT ?", (category, limit))
        debug(f"Querying questions for category: {category}", "database")
    else:
        # For admin interface, allow fetching all questions by setting a high limit
        if limit and limit > 1000:
            cursor.execute("SELECT * FROM questions ORDER BY id")
            debug("Querying all questions for admin interface", "database")
        else:
            cursor.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT ?", (limit,))
            debug(f"Querying random questions with limit: {limit}", "database")
    
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
    info(f"Returned {len(questions)} questions", "api")
    return questions

@app.post("/api/quiz/submit", response_model=QuizResult)
def submit_quiz(submission: QuizSubmission):
    """Submit quiz answers and get results"""
    info(f"Quiz submission received with {len(submission.answers)} answers", "quiz")
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
        debug(f"Retrieved correct answers for {len(db_correct_answers)} questions", "quiz")
    
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
    
    info(f"Quiz {quiz_id} completed: {correct_count}/{total_questions} ({score_percentage:.1f}%)", "quiz")
    
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
    info(f"Retrieving quiz result for ID: {quiz_id}", "api")
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM quiz_sessions WHERE id = ?", (quiz_id,))
    row = cursor.fetchone()
    
    if not row:
        warning(f"Quiz session not found: {quiz_id}", "api")
        raise HTTPException(status_code=404, detail="Quiz session not found")
    
    conn.close()
    debug(f"Quiz result retrieved successfully for: {quiz_id}", "api")
    
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
    info(f"Updating question {question_id}", "admin")
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    
    # First, check if the question exists
    cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        warning(f"Question not found for update: {question_id}", "admin")
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
            error(f"Invalid options count for question {question_id}: {len(question_update.options)}", "admin")
            raise HTTPException(status_code=400, detail="Question must have exactly 4 options")
        option_ids = [opt.id for opt in question_update.options]
        if len(set(option_ids)) != 4 or not all(id in ['a', 'b', 'c', 'd'] for id in option_ids):
            error(f"Invalid option IDs for question {question_id}: {option_ids}", "admin")
            raise HTTPException(status_code=400, detail="Options must have unique IDs 'a', 'b', 'c', 'd'")
        update_data["options"] = json.dumps([{"id": opt.id, "text": opt.text} for opt in question_update.options])
    if question_update.correct_answer is not None:
        # Validate correct answer
        if question_update.options:
            valid_ids = [opt.id for opt in question_update.options]
        else:
            valid_ids = [opt["id"] for opt in current_question["options"]]
        if question_update.correct_answer not in valid_ids:
            error(f"Invalid correct answer for question {question_id}: {question_update.correct_answer}", "admin")
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
        debug(f"Question {question_id} updated with fields: {list(update_data.keys())}", "admin")
    
    # Return updated question
    cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
    row = cursor.fetchone()
    conn.close()
    
    info(f"Question {question_id} update completed successfully", "admin")
    
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
    debug("Fetching available categories", "api")
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT category FROM questions")
    categories = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    info(f"Returned {len(categories)} categories", "api")
    return {"categories": categories}

@app.get("/api/questions/ai", response_model=List[Question])
def generate_ai_questions(subject: str, limit: Optional[int] = 5):
    """Generate AI-powered questions for a specific subject using Ollama"""
    info(f"AI question generation requested: subject={subject}, limit={limit}", "ai")
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

        debug(f"Calling Ollama with prompt for {subject}", "ai")
        # Call Ollama to generate questions
        response = ollama.chat(
            model='llama3.2',  # Using a common model, can be configurable
            messages=[{
                'role': 'user', 
                'content': prompt
            }]
        )
        
        # Parse the response
        try:
            questions_data = json.loads(response['message']['content'])
            
            # Ensure we have a list
            if not isinstance(questions_data, list):
                questions_data = [questions_data]
            
            # Convert to our format and add IDs
            questions = []
            for i, q_data in enumerate(questions_data[:limit]):
                # Validate the structure
                if not all(key in q_data for key in ['text', 'options', 'correct_answer']):
                    continue
                    
                questions.append({
                    "id": 1000 + i,  # Use high IDs to avoid conflicts with DB questions
                    "text": q_data["text"],
                    "options": q_data["options"],
                    "correct_answer": q_data["correct_answer"],
                    "category": subject.lower()
                })
            
            if not questions:
                error(f"No valid questions generated for subject: {subject}", "ai")
                raise ValueError("No valid questions generated")
            
            info(f"Successfully generated {len(questions)} AI questions for {subject}", "ai")
            return questions
            
        except json.JSONDecodeError:
            warning("JSON parsing failed, attempting to extract JSON from response", "ai")
            # If JSON parsing fails, try to extract JSON from the response
            content = response['message']['content']
            # Look for JSON array in the response
            start = content.find('[')
            end = content.rfind(']') + 1
            if start >= 0 and end > start:
                questions_data = json.loads(content[start:end])
                questions = []
                for i, q_data in enumerate(questions_data[:limit]):
                    if not all(key in q_data for key in ['text', 'options', 'correct_answer']):
                        continue
                    questions.append({
                        "id": 1000 + i,
                        "text": q_data["text"],
                        "options": q_data["options"],
                        "correct_answer": q_data["correct_answer"],
                        "category": subject.lower()
                    })
                info(f"Successfully extracted {len(questions)} AI questions for {subject}", "ai")
                return questions
            else:
                error(f"Could not parse AI response for subject: {subject}", "ai")
                raise ValueError("Could not parse AI response")
        
    except Exception as e:
        error(f"AI question generation failed for {subject}: {str(e)}", "ai")
        # If Ollama fails, return a fallback error
        raise HTTPException(
            status_code=503, 
            detail=f"AI question generation failed: {str(e)}. Please ensure Ollama is running and the llama3.2 model is available."
        )

@app.get("/api/logs")
def get_log_entries(
    limit: Optional[int] = 100,
    offset: Optional[int] = 0,
    level: Optional[str] = None,
    module: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
):
    """Get application logs with filtering and pagination"""
    info(f"Log retrieval requested: limit={limit}, offset={offset}, level={level}, module={module}", "logs")
    
    try:
        result = get_logs(
            limit=limit,
            offset=offset,
            level=level,
            module=module,
            start_time=start_time,
            end_time=end_time
        )
        debug(f"Retrieved {len(result['logs'])} log entries", "logs")
        return result
    except Exception as e:
        error(f"Failed to retrieve logs: {str(e)}", "logs")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve logs: {str(e)}")

@app.post("/api/logs/config")
def configure_logging(config: LogConfig):
    """Configure logging level dynamically"""
    info(f"Log level change requested: {config.level}", "config")
    
    try:
        from logger import set_log_level
        set_log_level(config.level)
        info(f"Log level changed to: {config.level}", "config")
        return {"message": f"Log level set to {config.level}", "level": config.level}
    except Exception as e:
        error(f"Failed to set log level: {str(e)}", "config")
        raise HTTPException(status_code=400, detail=f"Invalid log level: {config.level}")

if __name__ == "__main__":
    import uvicorn
    info("Starting Quizly API server", "startup")
    uvicorn.run(app, host="0.0.0.0", port=8000)