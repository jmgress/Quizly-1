from __future__ import annotations

import os
import json
import logging
from typing import List, Dict
from abc import ABC, abstractmethod

try:
    import ollama
except Exception:  # pragma: no cover - optional dependency
    ollama = None

try:
    import openai
except Exception:  # pragma: no cover - optional dependency
    openai = None

logger = logging.getLogger(__name__)

DEFAULT_PROMPT = (
    "Generate {limit} multiple-choice quiz questions about {subject}. "
    "Each question should have exactly 4 answer options labeled a, b, c, d. "
    "Format your response as a JSON array where each question has fields 'text',"
    " 'options', 'correct_answer', and 'category'. Return only the JSON array."
)


class LLMProvider(ABC):
    def __init__(self, model: str, prompt_template: str = DEFAULT_PROMPT) -> None:
        self.model = model
        self.prompt_template = prompt_template

    @abstractmethod
    def generate_questions(self, subject: str, limit: int) -> List[Dict]:
        pass

    def health_check(self) -> bool:
        """Check provider availability. Override if needed."""
        return True

    def _parse_response(self, content: str, subject: str, limit: int) -> List[Dict]:
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            start = content.find('[')
            end = content.rfind(']') + 1
            if start >= 0 and end > start:
                data = json.loads(content[start:end])
            else:
                raise ValueError("Could not parse AI response")

        if not isinstance(data, list):
            data = [data]

        questions = []
        for i, q in enumerate(data[:limit]):
            if not all(k in q for k in ['text', 'options', 'correct_answer']):
                continue
            questions.append({
                "id": 1000 + i,
                "text": q["text"],
                "options": q["options"],
                "correct_answer": q["correct_answer"],
                "category": subject.lower(),
            })
        if not questions:
            raise ValueError("No valid questions generated")
        return questions


class OllamaProvider(LLMProvider):
    def generate_questions(self, subject: str, limit: int) -> List[Dict]:
        if ollama is None:
            raise RuntimeError("Ollama package is not installed")
        prompt = self.prompt_template.format(subject=subject, limit=limit)
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response['message']['content']
        except Exception as e:
            logger.error("Ollama error: %s", e)
            raise RuntimeError(f"Ollama error: {e}")
        return self._parse_response(content, subject, limit)

    def health_check(self) -> bool:
        if ollama is None:
            return False
        try:
            ollama.list()
            return True
        except Exception:
            return False


class OpenAIProvider(LLMProvider):
    def __init__(self, model: str, api_key: str, prompt_template: str = DEFAULT_PROMPT) -> None:
        super().__init__(model, prompt_template)
        if openai is None:
            raise RuntimeError("openai package is not installed")
        openai.api_key = api_key

    def generate_questions(self, subject: str, limit: int) -> List[Dict]:
        if openai is None:
            raise RuntimeError("openai package is not installed")
        prompt = self.prompt_template.format(subject=subject, limit=limit)
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content
        except Exception as e:
            logger.error("OpenAI error: %s", e)
            raise RuntimeError(f"OpenAI error: {e}")
        return self._parse_response(content, subject, limit)

    def health_check(self) -> bool:
        if openai is None:
            return False
        try:
            openai.Model.list()
            return True
        except Exception:
            return False


def get_provider() -> LLMProvider:
    provider_name = os.getenv("LLM_PROVIDER", "ollama").lower()
    prompt_template = os.getenv("PROMPT_TEMPLATE", DEFAULT_PROMPT)

    if provider_name == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI provider")
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        logger.info("Using OpenAI provider with model %s", model)
        return OpenAIProvider(model=model, api_key=api_key, prompt_template=prompt_template)

    if provider_name == "ollama" or provider_name == "":
        model = os.getenv("OLLAMA_MODEL", "llama3.2")
        logger.info("Using Ollama provider with model %s", model)
        return OllamaProvider(model=model, prompt_template=prompt_template)

    raise ValueError(f"Unknown LLM_PROVIDER '{provider_name}'")
