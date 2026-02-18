from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import sys
import os
import json

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from main import app

client = TestClient(app)

@patch('sqlite3.connect')
def test_get_quiz_sessions(mock_connect):
    # Mock the database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Mock data
    mock_data = [
        ('id1', 10, 8, 80.0, '2023-01-01T10:00:00', '[{"question_id": 1, "is_correct": true}]'),
        ('id2', 5, 5, 100.0, '2023-01-02T10:00:00', '[{"question_id": 2, "is_correct": true}]')
    ]
    mock_cursor.fetchall.return_value = mock_data

    response = client.get("/api/quiz/sessions")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['id'] == 'id1'
    # Check that answers are parsed
    assert data[0]['answers'] == [{"question_id": 1, "is_correct": True}]

    # Verify the SQL query
    mock_cursor.execute.assert_called_with("SELECT * FROM quiz_sessions ORDER BY created_at DESC LIMIT ?", (100,))

@patch('sqlite3.connect')
def test_get_quiz_sessions_empty(mock_connect):
    # Mock the database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Mock empty data
    mock_cursor.fetchall.return_value = []

    response = client.get("/api/quiz/sessions")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
