"""Ollama provider implementation."""

from typing import List, Dict, Any
import json
import os
import logging

from .base import LLMProvider

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

        prompt = self._create_prompt(subject, limit)

        try:
            response = self._ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            return self._parse_response(response["message"]["content"], subject, limit)
        except Exception as e:
            logger.error(f"Ollama API call failed: {str(e)}")
            raise RuntimeError(f"Ollama question generation failed: {str(e)}")

    def health_check(self) -> bool:
        """Check if Ollama is available."""
        if not self._ollama:
            return False

        try:
            response = self._ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": "Test connection"}],
            )
            return "message" in response
        except Exception as e:
            logger.warning(f"Ollama health check failed: {str(e)}")
            return False

    def _create_prompt(self, subject: str, limit: int) -> str:
        return f"""Generate {limit} multiple-choice quiz questions about {subject}.\n        Each question should have exactly 4 answer options labeled a, b, c, d.\n        Format your response as a JSON array where each question has this structure:\n        {{\n            \"text\": \"question text here?\",\n            \"options\": [\n                {{\"id\": \"a\", \"text\": \"option A text\"}},\n                {{\"id\": \"b\", \"text\": \"option B text\"}},\n                {{\"id\": \"c\", \"text\": \"option C text\"}},\n                {{\"id\": \"d\", \"text\": \"option D text\"}}\n            ],\n            \"correct_answer\": \"a\",\n            \"category\": \"{subject.lower()}\"\n        }}\n\n        Return only the JSON array, no additional text."""

    def _parse_response(self, content: str, subject: str, limit: int) -> List[Dict[str, Any]]:
        try:
            questions_data = json.loads(content)
        except json.JSONDecodeError:
            start = content.find('[')
            end = content.rfind(']') + 1
            if start >= 0 and end > start:
                questions_data = json.loads(content[start:end])
            else:
                raise ValueError("Could not parse AI response as JSON")

        if not isinstance(questions_data, list):
            questions_data = [questions_data]

        questions = []
        for i, q_data in enumerate(questions_data[:limit]):
            if not all(key in q_data for key in ["text", "options", "correct_answer"]):
                continue
            questions.append(
                {
                    "id": 1000 + i,
                    "text": q_data["text"],
                    "options": q_data["options"],
                    "correct_answer": q_data["correct_answer"],
                    "category": subject.lower(),
                }
            )

        if not questions:
            raise ValueError("No valid questions generated")

        return questions
