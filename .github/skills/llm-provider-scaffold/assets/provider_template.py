"""Template for a new Quizly LLM provider.

Replace the following placeholders before use:
  <name>        -> lowercase provider id, e.g. "anthropic"
  <Name>        -> PascalCase class prefix, e.g. "Anthropic"
  <NAME>        -> UPPERCASE env prefix, e.g. "ANTHROPIC"
"""

from typing import List, Dict, Any
import os
import logging
import time

from .base import LLMProvider

logger = logging.getLogger(__name__)


class <Name>Provider(LLMProvider):
    """<Name> provider for question generation."""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("<NAME>_API_KEY")
        self.model = model or os.getenv("<NAME>_MODEL", "<default-model>")
        self._client = None
        self._initialize_client()

        try:
            from llm_prompt_logger import llm_prompt_logger
            self.prompt_logger = llm_prompt_logger
        except ImportError:
            logger.warning("LLM prompt logger not available")
            self.prompt_logger = None

    def _initialize_client(self):
        """Initialize the API client. Raise if the key is missing."""
        if not self.api_key:
            raise ValueError(
                "<Name> API key not provided. Set <NAME>_API_KEY environment variable."
            )
        try:
            # import <sdk>
            # self._client = <sdk>.Client(api_key=self.api_key)
            logger.info(f"<Name> provider initialized with model: {self.model}")
        except ImportError:
            logger.error("<Name> package not installed.")
            raise ImportError("<Name> package not available")

    def generate_questions(self, subject: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Generate questions using the <Name> API."""
        if not self._client:
            raise RuntimeError("<Name> client not initialized")

        prompt = self._create_prompt(subject, limit)
        start_time = time.time()
        try:
            # response = self._client.generate(model=self.model, prompt=prompt)
            # content = response.text
            content = ""  # TODO: call the API and extract text
            result = self._parse_response(content, subject, limit)

            if self.prompt_logger:
                self.prompt_logger.log_prompt(
                    provider="<name>",
                    model=self.model,
                    prompt=prompt,
                    response=content,
                    metadata={
                        "subject": subject,
                        "limit": limit,
                        "questions_generated": len(result),
                    },
                    timing={
                        "start_time": start_time,
                        "end_time": time.time(),
                        "duration_ms": round((time.time() - start_time) * 1000, 2),
                    },
                    level="INFO",
                )
            return result
        except Exception as e:
            if self.prompt_logger:
                self.prompt_logger.log_prompt(
                    provider="<name>",
                    model=self.model,
                    prompt=prompt,
                    metadata={"subject": subject, "limit": limit},
                    timing={
                        "start_time": start_time,
                        "end_time": time.time(),
                        "duration_ms": round((time.time() - start_time) * 1000, 2),
                    },
                    error=str(e),
                    level="ERROR",
                )
            # Do not include the API key in the error message.
            logger.error(f"<Name> API call failed: {str(e)}")
            raise RuntimeError(f"<Name> question generation failed: {str(e)}")

    def health_check(self) -> bool:
        """Return True if the provider is configured and reachable."""
        try:
            return self._client is not None
        except Exception:
            return False

    def _create_prompt(self, subject: str, limit: int) -> str:
        return (
            f"Generate {limit} multiple-choice quiz questions about {subject}. "
            "Return JSON with fields: text, options, correct_answer."
        )

    def _parse_response(self, content: str, subject: str, limit: int) -> List[Dict[str, Any]]:
        # TODO: parse `content` into a list of question dicts.
        raise NotImplementedError
