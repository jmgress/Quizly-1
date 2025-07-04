"""
OpenAI LLM Provider.
"""

import json
import os
import logging
from typing import List, Dict, Any

from .base_provider import LLMProvider

# Configure logging
# Use a child logger to inherit settings from the main llm_providers logger
logger = logging.getLogger(__name__).parent


class OpenAIProvider(LLMProvider):
    """OpenAI provider for question generation."""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._client = None
        self._initialize_openai()

    def _initialize_openai(self):
        """Initialize OpenAI client."""
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")

        try:
            import openai
            self._client = openai.OpenAI(api_key=self.api_key)
            logger.info(f"OpenAI provider initialized with model: {self.model}")
        except ImportError:
            logger.error("OpenAI package not installed. Install with: pip install openai")
            raise ImportError("OpenAI package not available")

    def generate_questions(self, subject: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Generate questions using OpenAI."""
        if not self._client:
            raise RuntimeError("OpenAI client not initialized")

        # Create the prompt
        prompt = self._create_prompt(subject, limit)

        try:
            # Call OpenAI API
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7,
                max_tokens=2000
            )

            # Parse and validate response
            content = response.choices[0].message.content
            return self._parse_response(content, subject, limit)

        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise RuntimeError(f"OpenAI question generation failed: {str(e)}")

    def health_check(self) -> bool:
        """Check if OpenAI API is available."""
        if not self._client:
            return False

        try:
            # Try a simple request to check connectivity
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=1
            )
            return response.choices[0].message.content is not None
        except Exception as e:
            logger.warning(f"OpenAI health check failed: {str(e)}")
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
        """Parse and validate the response from OpenAI."""
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
