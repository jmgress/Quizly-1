#!/usr/bin/env python3
"""Test script for logging functionality"""

import sys
import os
sys.path.append('/Users/james.m.gress/Reops/Quizly-1/backend')

# Test our logging setup
from main import setup_logging
import logging

# Setup logging
setup_logging()
logger = logging.getLogger('test_logging')

# Test different log levels
logger.debug("Debug message - detailed information")
logger.info("Info message - general information")
logger.warning("Warning message - something unexpected happened")
logger.error("Error message - something went wrong")

print("✅ Logging test completed!")
print("Check the log files in /Users/james.m.gress/Reops/Quizly-1/logs/backend/")
