#!/usr/bin/env python3
"""Test script for logging functionality"""

import sys
import os

# Add project root to sys.path to allow backend imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Test our logging setup
from backend.main import setup_logging
import logging

# Setup logging
setup_logging() # This might need to be called carefully if it configures global state
logger = logging.getLogger('test_logging')

# Test different log levels
logger.debug("Debug message - detailed information")
logger.info("Info message - general information")
logger.warning("Warning message - something unexpected happened")
logger.error("Error message - something went wrong")

print("✅ Logging test completed!")
print("Check the log files (typically in a 'logs/backend/' directory configured in logging_config.json).")
