from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import json
import uuid
from datetime import datetime
import requests

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

class QuizAnswer(BaseModel):
    question_id: int
    selected_answer: str

class QuizSubmission(BaseModel):
    answers: List[QuizAnswer]

class QuizResult(BaseModel):
    quiz_id: str
    total_questions: int
    correct_answers: int
    score_percentage: float
    answers: List[dict]

class GenerateQuestionRequest(BaseModel):
    """Request body for AI question generation"""
    category: str
    model: Optional[str] = "llama2"

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


@app.post("/api/questions/generate", response_model=Question)
def generate_question(req: GenerateQuestionRequest):
    """Generate a quiz question using the Ollama LLM"""
    prompt = (
        f"Generate a multiple-choice question about {req.category}. "
        "Return JSON with keys 'text', 'options', 'correct_answer'. "
        "Options should be an array of four objects with 'id' (a-d) and 'text'."
    )

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": req.model, "prompt": prompt},
            timeout=30,
        )
        response.raise_for_status()
        data_text = response.json().get("response", "")
        data = json.loads(data_text)
        if "category" not in data:
            data["category"] = req.category
        return Question(
            id=0,
            text=data["text"],
            options=data["options"],
            correct_answer=data["correct_answer"],
            category=data.get("category", req.category),
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail="LLM service unavailable") from e

@app.post("/api/quiz/submit", response_model=QuizResult)
def submit_quiz(submission: QuizSubmission):
    """Submit quiz answers and get results"""
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    
    # Get correct answers for submitted questions
    question_ids = [answer.question_id for answer in submission.answers]
    placeholders = ','.join(['?'] * len(question_ids))
    cursor.execute(f"SELECT id, correct_answer FROM questions WHERE id IN ({placeholders})", question_ids)
    
    correct_answers_map = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Calculate score
    correct_count = 0
    answer_details = []
    
    for answer in submission.answers:
        is_correct = correct_answers_map.get(answer.question_id) == answer.selected_answer
        if is_correct:
            correct_count += 1
        
        answer_details.append({
            "question_id": answer.question_id,
            "selected_answer": answer.selected_answer,
            "correct_answer": correct_answers_map.get(answer.question_id),
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

@app.get("/api/categories")
def get_categories():
    """Get available quiz categories"""
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT category FROM questions")
    categories = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return {"categories": categories}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)