"""Test security protections against SQL injection vulnerabilities.

This module tests that the API endpoints are protected against SQL injection
attacks in:
- The dynamic UPDATE query in update_question (column-name allowlist)
- The dynamic IN clause in submit_quiz (parameterized placeholders)
"""

import pytest
import sys
import os
import sqlite3
import json
from unittest.mock import patch
from fastapi.testclient import TestClient

# Add backend directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

# Keep a reference to the real connect before any patching
_real_sqlite3_connect = sqlite3.connect


# ---------------------------------------------------------------------------
# Helper: build a minimal test database
# ---------------------------------------------------------------------------

def _create_test_db(db_path):
    """Create a minimal SQLite DB with one sample question."""
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


def _make_app_client(db_path):
    """Return a TestClient that redirects all sqlite3.connect calls to db_path."""
    # Use the saved real connect to avoid infinite recursion
    with patch("sqlite3.connect", side_effect=lambda _: _real_sqlite3_connect(db_path)):
        from main import app
        return TestClient(app)


# ---------------------------------------------------------------------------
# Tests for the UPDATE column-name allowlist
# ---------------------------------------------------------------------------

class TestUpdateQuestionColumnAllowlist:
    """Tests ensuring the column allowlist blocks SQL injection in UPDATE."""

    def test_valid_update_text(self, tmp_path):
        """A legitimate text update should succeed."""
        db_path = str(tmp_path / "quiz.db")
        _create_test_db(db_path)

        with patch("sqlite3.connect", side_effect=lambda _: _real_sqlite3_connect(db_path)):
            from main import app
            client = TestClient(app)
            response = client.put(
                "/api/questions/1",
                json={"text": "Updated question text?"},
            )
        assert response.status_code == 200
        assert response.json()["text"] == "Updated question text?"

    def test_valid_update_category(self, tmp_path):
        """A legitimate category update should succeed."""
        db_path = str(tmp_path / "quiz.db")
        _create_test_db(db_path)

        with patch("sqlite3.connect", side_effect=lambda _: _real_sqlite3_connect(db_path)):
            from main import app
            client = TestClient(app)
            response = client.put(
                "/api/questions/1",
                json={"category": "science"},
            )
        assert response.status_code == 200
        assert response.json()["category"] == "science"

    def test_valid_update_correct_answer(self, tmp_path):
        """A legitimate correct_answer update should succeed."""
        db_path = str(tmp_path / "quiz.db")
        _create_test_db(db_path)

        with patch("sqlite3.connect", side_effect=lambda _: _real_sqlite3_connect(db_path)):
            from main import app
            client = TestClient(app)
            response = client.put(
                "/api/questions/1",
                json={"correct_answer": "a"},
            )
        assert response.status_code == 200
        assert response.json()["correct_answer"] == "a"

    def test_sql_injection_in_column_name_is_blocked(self, tmp_path):
        """
        Sending an unrecognised field should not reach the DB.

        The Pydantic model (QuestionUpdate) only allows text, options,
        correct_answer, and category.  Any extra keys are silently ignored by
        Pydantic, so the update_data dict will never contain them.  This test
        confirms that a malicious extra field cannot reach the SQL layer.
        """
        db_path = str(tmp_path / "quiz.db")
        _create_test_db(db_path)

        with patch("sqlite3.connect", side_effect=lambda _: _real_sqlite3_connect(db_path)):
            from main import app
            client = TestClient(app)
            # Inject a malicious key via JSON — Pydantic will strip unknown fields
            response = client.put(
                "/api/questions/1",
                json={"text": "Safe update", "malicious_col; DROP TABLE questions; --": "evil"},
            )
        # The request should succeed (malicious key silently dropped by Pydantic)
        # and the questions table should still exist
        assert response.status_code == 200
        conn = _real_sqlite3_connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='questions'")
        assert cursor.fetchone() is not None, "questions table must still exist"
        conn.close()

    def test_update_with_no_fields_is_no_op(self, tmp_path):
        """Sending an empty update body returns the unchanged question."""
        db_path = str(tmp_path / "quiz.db")
        _create_test_db(db_path)

        with patch("sqlite3.connect", side_effect=lambda _: _real_sqlite3_connect(db_path)):
            from main import app
            client = TestClient(app)
            response = client.put("/api/questions/1", json={})
        assert response.status_code == 200
        assert response.json()["text"] == "What is the capital of France?"


# ---------------------------------------------------------------------------
# Tests for the submit_quiz IN-clause parameterisation
# ---------------------------------------------------------------------------

class TestSubmitQuizInClause:
    """Tests ensuring the IN clause in submit_quiz uses safe parameterization."""

    def test_submit_quiz_returns_correct_score(self, tmp_path):
        """Submitting a correct answer returns a 100% score."""
        db_path = str(tmp_path / "quiz.db")
        _create_test_db(db_path)

        with patch("sqlite3.connect", side_effect=lambda _: _real_sqlite3_connect(db_path)):
            from main import app
            client = TestClient(app)
            response = client.post(
                "/api/quiz/submit",
                json={"answers": [{"question_id": 1, "selected_answer": "c"}]},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["score_percentage"] == 100.0
        assert data["correct_answers"] == 1

    def test_submit_quiz_with_wrong_answer(self, tmp_path):
        """Submitting a wrong answer returns a 0% score."""
        db_path = str(tmp_path / "quiz.db")
        _create_test_db(db_path)

        with patch("sqlite3.connect", side_effect=lambda _: _real_sqlite3_connect(db_path)):
            from main import app
            client = TestClient(app)
            response = client.post(
                "/api/quiz/submit",
                json={"answers": [{"question_id": 1, "selected_answer": "a"}]},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["score_percentage"] == 0.0
        assert data["correct_answers"] == 0

    def test_submit_quiz_with_nonexistent_question_id(self, tmp_path):
        """
        Submitting answers for question IDs that don't exist should not crash.
        The score falls back to the client-supplied correct_answer field.
        """
        db_path = str(tmp_path / "quiz.db")
        _create_test_db(db_path)

        with patch("sqlite3.connect", side_effect=lambda _: _real_sqlite3_connect(db_path)):
            from main import app
            client = TestClient(app)
            response = client.post(
                "/api/quiz/submit",
                json={
                    "answers": [
                        {
                            "question_id": 9999,
                            "selected_answer": "b",
                            "correct_answer": "b",
                        }
                    ]
                },
            )
        assert response.status_code == 200

    def test_submit_quiz_empty_answers_handled_gracefully(self, tmp_path):
        """Submitting an empty answers list returns a 0% score without crashing."""
        db_path = str(tmp_path / "quiz.db")
        _create_test_db(db_path)

        with patch("sqlite3.connect", side_effect=lambda _: _real_sqlite3_connect(db_path)):
            from main import app
            client = TestClient(app)
            response = client.post("/api/quiz/submit", json={"answers": []})
        assert response.status_code == 200
        assert response.json()["score_percentage"] == 0.0

    def test_submit_quiz_multiple_questions(self, tmp_path):
        """Multiple question IDs in the IN clause are all resolved correctly."""
        db_path = str(tmp_path / "quiz.db")
        _create_test_db(db_path)

        # Add a second question to the DB
        conn = _real_sqlite3_connect(db_path)
        cur = conn.cursor()
        opts2 = json.dumps([
            {"id": "a", "text": "Mars"},
            {"id": "b", "text": "Venus"},
            {"id": "c", "text": "Jupiter"},
            {"id": "d", "text": "Saturn"},
        ])
        cur.execute(
            "INSERT INTO questions (text, options, correct_answer, category) VALUES (?, ?, ?, ?)",
            ("Which planet is the Red Planet?", opts2, "a", "science"),
        )
        conn.commit()
        conn.close()

        with patch("sqlite3.connect", side_effect=lambda _: _real_sqlite3_connect(db_path)):
            from main import app
            client = TestClient(app)
            response = client.post(
                "/api/quiz/submit",
                json={
                    "answers": [
                        {"question_id": 1, "selected_answer": "c"},  # correct
                        {"question_id": 2, "selected_answer": "a"},  # correct
                    ]
                },
            )
        assert response.status_code == 200
        data = response.json()
        assert data["correct_answers"] == 2
        assert data["score_percentage"] == 100.0
