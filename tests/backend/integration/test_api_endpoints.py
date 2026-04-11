"""Tests for API endpoint logging and basic responses."""

import pytest
import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from main import app, setup_logging
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    setup_logging()
    return TestClient(app)


def test_root_endpoint(client):
    """Test that the root endpoint returns a 200 response."""
    response = client.get("/")
    assert response.status_code == 200


def test_health_endpoint(client):
    """Test that the health endpoint returns a 200 response."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


def test_questions_endpoint(client):
    """Test that the questions endpoint returns a list."""
    response = client.get("/api/questions?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
