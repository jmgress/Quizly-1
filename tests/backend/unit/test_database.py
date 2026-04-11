"""Tests for basic database functionality."""

import pytest
import sqlite3
import json


def test_database(tmp_path):
    """Test database creation, insertion, and retrieval."""
    db_path = str(tmp_path / "test_quiz.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            options TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            category TEXT DEFAULT 'general'
        )"""
    )

    sample_question = {
        "text": "What is the capital of France?",
        "options": [
            {"id": "a", "text": "London"},
            {"id": "b", "text": "Berlin"},
            {"id": "c", "text": "Paris"},
            {"id": "d", "text": "Madrid"},
        ],
        "correct_answer": "c",
        "category": "geography",
    }

    cursor.execute(
        "INSERT INTO questions (text, options, correct_answer, category) VALUES (?, ?, ?, ?)",
        (
            sample_question["text"],
            json.dumps(sample_question["options"]),
            sample_question["correct_answer"],
            sample_question["category"],
        ),
    )
    conn.commit()

    cursor.execute("SELECT * FROM questions")
    row = cursor.fetchone()
    conn.close()

    assert row is not None, "Expected a row in the questions table"
    assert row[1] == "What is the capital of France?"
    assert json.loads(row[2]) == sample_question["options"]
    assert row[3] == "c"
    assert row[4] == "geography"


def test_quiz_logic():
    """Test quiz scoring calculation."""
    answers = [
        {"question_id": 1, "selected_answer": "c"},  # correct
        {"question_id": 2, "selected_answer": "a"},  # incorrect
    ]
    correct_answers_map = {1: "c", 2: "b"}

    correct_count = sum(
        1
        for answer in answers
        if correct_answers_map.get(answer["question_id"]) == answer["selected_answer"]
    )

    total_questions = len(answers)
    score_percentage = (correct_count / total_questions) * 100

    assert correct_count == 1
    assert total_questions == 2
    assert score_percentage == 50.0