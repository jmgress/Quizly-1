"""OpenAI provider implementation."""

from typing import List, Dict, Any
import json
import os
import logging
import time

from .base import LLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI provider for question generation."""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._client = None
        self._initialize_openai()
        
        # Initialize LLM prompt logger
        try:
            from llm_prompt_logger import llm_prompt_logger
            self.prompt_logger = llm_prompt_logger
        except ImportError:
            logger.warning("LLM prompt logger not available")
            self.prompt_logger = None

    def _initialize_openai(self):
        """Initialize OpenAI client."""
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable."
            )

        try:
            import openai
            self._client = openai.OpenAI(api_key=self.api_key)
            logger.info(f"OpenAI provider initialized with model: {self.model}")
        except ImportError:
            logger.error("OpenAI package not installed. Install with: pip install openai")
            raise ImportError("OpenAI package not available")

    def generate_questions(self, subject: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Generate questions using OpenAI."""
        if not self._client:
            raise RuntimeError("OpenAI client not initialized")

        prompt = self._create_prompt(subject, limit)
        start_time = time.time()

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000,
            )
            
            end_time = time.time()
            content = response.choices[0].message.content
            result = self._parse_response(content, subject, limit)
            
            # Log successful interaction
            if self.prompt_logger:
                self.prompt_logger.log_prompt(
                    provider="openai",
                    model=self.model,
                    prompt=prompt,
                    response=content,
                    metadata={
                        "subject": subject,
                        "limit": limit,
                        "questions_generated": len(result),
                        "temperature": 0.7,
                        "max_tokens": 2000
                    },
                    timing={
                        "start_time": start_time,
                        "end_time": end_time,
                        "duration_ms": round((end_time - start_time) * 1000, 2)
                    },
                    level="INFO"
                )
            
            return result
            
        except Exception as e:
            end_time = time.time()
            
            # Log failed interaction
            if self.prompt_logger:
                self.prompt_logger.log_prompt(
                    provider="openai",
                    model=self.model,
                    prompt=prompt,
                    metadata={
                        "subject": subject,
                        "limit": limit,
                        "temperature": 0.7,
                        "max_tokens": 2000
                    },
                    timing={
                        "start_time": start_time,
                        "end_time": end_time,
                        "duration_ms": round((end_time - start_time) * 1000, 2)
                    },
                    error=str(e),
                    level="ERROR"
                )
            
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise RuntimeError(f"OpenAI question generation failed: {str(e)}")

    def health_check(self) -> bool:
        """Check if OpenAI API is available."""
        if not self._client:
            return False

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=1,
            )
            return response.choices[0].message.content is not None
        except Exception as e:
            logger.warning(f"OpenAI health check failed: {str(e)}")
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
