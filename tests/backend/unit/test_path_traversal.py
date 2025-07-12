import os
import sys
from fastapi.testclient import TestClient

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))
from main import app

client = TestClient(app)

def test_download_log_file_path_traversal():
    response = client.get('/api/logging/files/../secret.txt/download')
    assert response.status_code == 400

