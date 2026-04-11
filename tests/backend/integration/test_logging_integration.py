"""Tests for logging setup functionality."""

import pytest
import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))


def test_setup_logging():
    """Test that setup_logging configures logging without errors."""
    from main import setup_logging

    setup_logging()

    logger = logging.getLogger("test_logging")

    # Verify that logging at all levels completes without raising exceptions
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

    # Confirm a logger instance was returned
    assert logger is not None
    assert isinstance(logger, logging.Logger)
