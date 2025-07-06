#!/usr/bin/env python3
"""Shared helper utilities for tests."""

import sys
import os
import logging

# Add backend directory to Python path so helpers can import backend modules
BACKEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../backend')
)
sys.path.append(BACKEND_DIR)

from main import setup_logging


def demo_logging() -> None:
    """Initialize logging and emit sample log messages."""
    setup_logging()
    logger = logging.getLogger('test_logging')
    logger.debug("Debug message - detailed information")
    logger.info("Info message - general information")
    logger.warning("Warning message - something unexpected happened")
    logger.error("Error message - something went wrong")


__all__ = ["demo_logging"]

print("✅ Logging test completed!")
print("Check the log files in /Users/james.m.gress/Reops/Quizly-1/logs/backend/")
