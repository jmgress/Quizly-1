"""
Base LLM Provider definition.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate_questions(self, subject: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Generate quiz questions for a given subject.

        Args:
            subject: The subject/topic for the questions
            limit: Number of questions to generate

        Returns:
            List of question dictionaries with required fields
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if the provider is available and working."""
        pass
