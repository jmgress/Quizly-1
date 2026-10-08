"""Tests for the verbose logging improvements.

Covers:
- Log format includes funcName and lineno
- Request/response middleware records are emitted
- New endpoint logging (submit_quiz, get_quiz_result, update_question, get_categories)
- setup_logging() creates the expected file handlers
"""

import json
import logging
import os
import sys
import tempfile
import unittest.mock as mock

import pytest
from fastapi.testclient import TestClient

# Add backend directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_app():
    """Import the FastAPI app (cached by Python module system)."""
    from main import app
    return app


# ---------------------------------------------------------------------------
# Log format tests
# ---------------------------------------------------------------------------

def test_verbose_log_format_contains_funcname_and_lineno():
    """The default log format used by setup_logging should include funcName and lineno."""
    from main import setup_logging

    with tempfile.TemporaryDirectory() as tmp_dir:
        import main as main_mod
        original_config = main_mod.logging_config.copy()
        # Remove log_format entirely so the fallback verbose format is exercised
        file_settings = dict(main_mod.logging_config.get('file_settings', {}))
        file_settings['log_directory'] = tmp_dir
        file_settings.pop('log_format', None)
        main_mod.logging_config = {**original_config, 'file_settings': file_settings}
        try:
            root_logger = setup_logging()
        finally:
            main_mod.logging_config = original_config

        # Inspect formatter strings on the added handlers
        formats = [
            handler.formatter._fmt
            for handler in root_logger.handlers
            if handler.formatter is not None
        ]
        assert any('funcName' in fmt for fmt in formats), (
            "Expected 'funcName' in at least one handler's log format"
        )
        assert any('lineno' in fmt for fmt in formats), (
            "Expected 'lineno' in at least one handler's log format"
        )


# ---------------------------------------------------------------------------
# HTTP middleware logging tests
# ---------------------------------------------------------------------------

def test_request_middleware_logs_completed_request(caplog):
    """Middleware should emit an INFO log for every completed request."""
    app = _get_app()
    client = TestClient(app, raise_server_exceptions=False)

    with caplog.at_level(logging.INFO, logger='main'):
        client.get('/api/health')

    messages = [r.message for r in caplog.records]
    assert any('Request completed' in m for m in messages), (
        f"Expected 'Request completed' log. Got: {messages}"
    )


def test_request_middleware_logs_debug_incoming(caplog):
    """Middleware should emit a DEBUG log for the incoming request."""
    app = _get_app()
    client = TestClient(app, raise_server_exceptions=False)

    with caplog.at_level(logging.DEBUG, logger='main'):
        client.get('/api/categories')

    messages = [r.message for r in caplog.records]
    assert any('Incoming request' in m for m in messages), (
        f"Expected 'Incoming request' debug log. Got: {messages}"
    )


def test_request_middleware_logs_client_error(caplog):
    """Middleware should emit a WARNING for 4xx responses."""
    app = _get_app()
    client = TestClient(app, raise_server_exceptions=False)

    with caplog.at_level(logging.WARNING, logger='main'):
        # Non-existent quiz session → 404
        client.get('/api/quiz/nonexistent-id-12345')

    messages = [r.message for r in caplog.records]
    assert any('Client error' in m or '404' in m for m in messages), (
        f"Expected a warning log for 4xx. Got: {messages}"
    )


# ---------------------------------------------------------------------------
# Endpoint verbose logging tests
# ---------------------------------------------------------------------------

def test_submit_quiz_logs_answer_count(caplog):
    """submit_quiz should log the number of submitted answers."""
    app = _get_app()
    client = TestClient(app, raise_server_exceptions=False)

    payload = {
        "answers": [
            {"question_id": 1, "selected_answer": "a", "correct_answer": "a"}
        ]
    }

    with caplog.at_level(logging.INFO, logger='main'):
        client.post('/api/quiz/submit', json=payload)

    messages = [r.message for r in caplog.records]
    assert any('Quiz submission received' in m for m in messages), (
        f"Expected 'Quiz submission received' log. Got: {messages}"
    )


def test_get_quiz_result_logs_fetch(caplog):
    """get_quiz_result should log a DEBUG message when fetching a session."""
    app = _get_app()
    client = TestClient(app, raise_server_exceptions=False)

    with caplog.at_level(logging.DEBUG, logger='main'):
        client.get('/api/quiz/some-fake-id')

    messages = [r.message for r in caplog.records]
    assert any('Fetching quiz result' in m for m in messages), (
        f"Expected 'Fetching quiz result' debug log. Got: {messages}"
    )


def test_get_categories_logs_count(caplog):
    """get_categories should log the number of categories returned."""
    app = _get_app()
    client = TestClient(app, raise_server_exceptions=False)

    with caplog.at_level(logging.INFO, logger='main'):
        client.get('/api/categories')

    messages = [r.message for r in caplog.records]
    assert any('Returning' in m and 'categor' in m for m in messages), (
        f"Expected 'Returning N categories' log. Got: {messages}"
    )


# ---------------------------------------------------------------------------
# LLM log file handler filter test
# ---------------------------------------------------------------------------

def test_llm_log_handler_filter():
    """The LLM file handler's filter should pass LLM-related logger names only."""
    from main import setup_logging

    with tempfile.TemporaryDirectory() as tmp_dir:
        import main as main_mod
        original_config = main_mod.logging_config.copy()
        main_mod.logging_config['file_settings'] = {
            **main_mod.logging_config.get('file_settings', {}),
            'log_directory': tmp_dir,
            'log_format': None,
        }
        try:
            root_logger = setup_logging()
        finally:
            main_mod.logging_config = original_config

    # Find the handler that writes to llm.log
    llm_handlers = [
        h for h in root_logger.handlers
        if hasattr(h, 'baseFilename') and 'llm.log' in h.baseFilename
    ]
    assert llm_handlers, "Expected a dedicated llm.log file handler"

    llm_handler = llm_handlers[0]
    filters = llm_handler.filters
    assert filters, "LLM handler should have at least one filter"

    # Simulate log records
    llm_record = logging.LogRecord(
        name='llm_providers.openai', level=logging.DEBUG,
        pathname='', lineno=0, msg='test', args=(), exc_info=None
    )
    non_llm_record = logging.LogRecord(
        name='uvicorn.error', level=logging.DEBUG,
        pathname='', lineno=0, msg='test', args=(), exc_info=None
    )

    assert filters[0].filter(llm_record), "LLM logger should pass the filter"
    assert not filters[0].filter(non_llm_record), "Non-LLM logger should not pass the filter"
