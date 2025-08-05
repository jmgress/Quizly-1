"""Base definitions for LLM providers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate_questions(self, subject: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Generate quiz questions for a given subject."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if the provider is available and working."""
        pass
