#!/usr/bin/env python3
"""Test endpoint calls to verify logging"""

import sys
import os
import time

# Add project root to sys.path to allow backend imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.main import app, setup_logging
from fastapi.testclient import TestClient
import logging

# Setup logging
setup_logging() # This might need to be called carefully if it configures global state
logger = logging.getLogger('endpoint_test')

# Create test client
client = TestClient(app)

logger.info("Starting endpoint tests...")

# Test the root endpoint
try:
    response = client.get("/")
    logger.info(f"Root endpoint response: {response.status_code}")
    logger.info(f"Root endpoint body: {response.json()}")
except Exception as e:
    logger.error(f"Error testing root endpoint: {e}")

# Test the health endpoint
try:
    response = client.get("/api/health")
    logger.info(f"Health endpoint response: {response.status_code}")
    logger.info(f"Health endpoint body: {response.json()}")
except Exception as e:
    logger.error(f"Error testing health endpoint: {e}")

# Test the questions endpoint
try:
    response = client.get("/api/questions?limit=5")
    logger.info(f"Questions endpoint response: {response.status_code}")
    data = response.json()
    logger.info(f"Questions endpoint returned {len(data)} questions")
except Exception as e:
    logger.error(f"Error testing questions endpoint: {e}")

logger.info("Endpoint tests completed!")
print("✅ All endpoint tests completed!")
print("Check the log files (typically in a 'logs/backend/' directory configured in logging_config.json).")
