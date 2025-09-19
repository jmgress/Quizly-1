"""Full workflow integration tests for the Quizly application."""

import pytest
import requests
import time
import os
import sys

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

# Test configuration
API_BASE_URL = "http://localhost:8000"

class TestFullWorkflow:
    """Test complete user workflows."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test."""
        # Setup: Ensure API is running (skip if not available)
        try:
            response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
            if response.status_code != 200:
                pytest.skip("API server not available")
        except requests.exceptions.RequestException:
            pytest.skip("API server not available")
        
        yield
        
        # Teardown: Any cleanup if needed
        pass
    
    def test_complete_quiz_workflow_database(self):
        """Test complete quiz workflow using database questions."""
        # 1. Get available categories
        response = requests.get(f"{API_BASE_URL}/api/categories")
        assert response.status_code == 200
        categories = response.json()
        assert len(categories) > 0
        
        # 2. Get questions for a category
        category = categories[0]
        response = requests.get(f"{API_BASE_URL}/api/questions?category={category}&limit=10")
        assert response.status_code == 200
        questions = response.json()
        assert len(questions) > 0
        
        # 3. Simulate answering questions
        answers = []
        for question in questions:
            # Select first option as answer (simplified)
            answers.append({
                "question_id": question["id"],
                "selected_answer": question["options"][0]["id"]
            })
        
        # 4. Submit quiz results (if endpoint exists)
        # This would be implemented when quiz submission endpoint is added
        pass
    
    def test_complete_quiz_workflow_ai(self):
        """Test complete quiz workflow using AI-generated questions."""
        # Skip if AI is not configured
        try:
            response = requests.get(f"{API_BASE_URL}/api/questions/ai?subject=python&limit=2", timeout=10)
            if response.status_code != 200:
                pytest.skip("AI question generation not available")
        except requests.exceptions.RequestException:
            pytest.skip("AI question generation not available")
        
        # 1. Request AI questions
        response = requests.get(f"{API_BASE_URL}/api/questions/ai?subject=python&limit=3")
        assert response.status_code == 200
        questions = response.json()
        assert len(questions) > 0
        
        # 2. Verify question structure
        for question in questions:
            assert "text" in question
            assert "options" in question
            assert "correct_answer" in question
            assert len(question["options"]) > 0
    
    def test_logging_configuration_workflow(self):
        """Test logging configuration workflow."""
        # 1. Get current logging config
        response = requests.get(f"{API_BASE_URL}/api/logging/config")
        assert response.status_code == 200
        current_config = response.json()
        
        # 2. Update logging config
        new_config = {
            "level": "DEBUG",
            "format": "%(asctime)s - %(levelname)s - %(message)s"
        }
        response = requests.post(f"{API_BASE_URL}/api/logging/config", json=new_config)
        assert response.status_code == 200
        
        # 3. Verify config was updated
        response = requests.get(f"{API_BASE_URL}/api/logging/config")
        assert response.status_code == 200
        updated_config = response.json()
        assert updated_config["level"] == "DEBUG"
        
        # 4. Reset to original config
        response = requests.post(f"{API_BASE_URL}/api/logging/config", json=current_config)
        assert response.status_code == 200
    
    def test_llm_configuration_workflow(self):
        """Test LLM configuration workflow."""
        # 1. Get current LLM config
        response = requests.get(f"{API_BASE_URL}/api/llm/config")
        assert response.status_code == 200
        current_config = response.json()
        
        # 2. Update LLM provider (if endpoint exists)
        # This would test switching between OpenAI and Ollama
        # Implementation depends on actual API design
        pass
    
    def test_error_handling_workflow(self):
        """Test error handling in various scenarios."""
        # 1. Test invalid category
        response = requests.get(f"{API_BASE_URL}/api/questions?category=invalid_category")
        # Should handle gracefully (empty list or appropriate error)
        assert response.status_code in [200, 404]
        
        # 2. Test invalid question limit
        response = requests.get(f"{API_BASE_URL}/api/questions?limit=1000")
        # Should handle large limits gracefully
        assert response.status_code == 200
        
        # 3. Test malformed requests
        response = requests.get(f"{API_BASE_URL}/api/questions?invalid_param=test")
        # Should ignore invalid parameters
        assert response.status_code == 200

if __name__ == "__main__":
    # Allow running individual tests
    pytest.main([__file__, "-v"])