"""Shared pytest configuration and fixtures for backend tests."""

import os
import sys
import json
import sqlite3
import pytest

# Add backend directory to path for all backend tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

# Keep a reference to the real sqlite3.connect before any test patching
_real_sqlite3_connect = sqlite3.connect


@pytest.fixture
def sample_db(tmp_path):
    """Fixture that creates a minimal SQLite test database."""
    db_path = str(tmp_path / "quiz.db")
    conn = _real_sqlite3_connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            options TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            category TEXT DEFAULT 'general'
        )"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS quiz_sessions (
            id TEXT PRIMARY KEY,
            total_questions INTEGER,
            correct_answers INTEGER,
            score_percentage REAL,
            created_at TEXT,
            answers TEXT
        )"""
    )
    sample_options = json.dumps([
        {"id": "a", "text": "London"},
        {"id": "b", "text": "Berlin"},
        {"id": "c", "text": "Paris"},
        {"id": "d", "text": "Madrid"},
    ])
    cur.execute(
        "INSERT INTO questions (text, options, correct_answer, category) VALUES (?, ?, ?, ?)",
        ("What is the capital of France?", sample_options, "c", "geography"),
    )
    conn.commit()
    conn.close()
    return db_path
