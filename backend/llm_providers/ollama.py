"""
Ollama provider for local LLM question generation.
"""

from typing import List, Dict, Any
import json
import logging

from .base import LLMProvider

# Configure logging
logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """Ollama provider for local LLM question generation."""
    
    def __init__(self, model: str = "llama3.2", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host
        self._ollama = None
        self._initialize_ollama()
    
    def _initialize_ollama(self):
        """Initialize Ollama client."""
        try:
            import ollama
            self._ollama = ollama
            logger.info(f"Ollama provider initialized with model: {self.model}")
        except ImportError:
            logger.error("Ollama package not installed. Install with: pip install ollama")
            raise ImportError("Ollama package not available")
    
    def generate_questions(self, subject: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Generate questions using Ollama."""
        if not self._ollama:
            raise RuntimeError("Ollama client not initialized")
        
        # Create the prompt template
        prompt = self._create_prompt(subject, limit)
        
        try:
            # Call Ollama API
            response = self._ollama.chat(
                model=self.model,
                messages=[{
                    'role': 'user', 
                    'content': prompt
                }]
            )
            
            # Parse and validate response
            return self._parse_response(response['message']['content'], subject, limit)
            
        except Exception as e:
            logger.error(f"Ollama API call failed: {str(e)}")
            raise RuntimeError(f"Ollama question generation failed: {str(e)}")
    
    def health_check(self) -> bool:
        """Check if Ollama is available."""
        if not self._ollama:
            return False
        
        try:
            # Try a simple request to check connectivity
            response = self._ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': 'Test connection'}]
            )
            return 'message' in response
        except Exception as e:
            logger.warning(f"Ollama health check failed: {str(e)}")
            return False
    
    def _create_prompt(self, subject: str, limit: int) -> str:
        """Create the prompt for question generation."""
        return f"""Generate {limit} multiple-choice quiz questions about {subject}. 
        Each question should have exactly 4 answer options labeled a, b, c, d.
        Format your response as a JSON array where each question has this structure:
        {{
            "text": "question text here?",
            "options": [
                {{"id": "a", "text": "option A text"}},
                {{"id": "b", "text": "option B text"}},
                {{"id": "c", "text": "option C text"}},
                {{"id": "d", "text": "option D text"}}
            ],
            "correct_answer": "a",
            "category": "{subject.lower()}"
        }}
        
        Return only the JSON array, no additional text."""
    
    def _parse_response(self, content: str, subject: str, limit: int) -> List[Dict[str, Any]]:
        """Parse and validate the response from Ollama."""
        try:
            questions_data = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            start = content.find('[')
            end = content.rfind(']') + 1
            if start >= 0 and end > start:
                questions_data = json.loads(content[start:end])
            else:
                raise ValueError("Could not parse AI response as JSON")
        
        # Ensure we have a list
        if not isinstance(questions_data, list):
            questions_data = [questions_data]
        
        # Validate and format questions
        questions = []
        for i, q_data in enumerate(questions_data[:limit]):
            if not all(key in q_data for key in ['text', 'options', 'correct_answer']):
                continue
                
            questions.append({
                "id": 1000 + i,  # Use high IDs to avoid conflicts with DB questions
                "text": q_data["text"],
                "options": q_data["options"],
                "correct_answer": q_data["correct_answer"],
                "category": subject.lower()
            })
        
        if not questions:
            raise ValueError("No valid questions generated")
        
        return questions