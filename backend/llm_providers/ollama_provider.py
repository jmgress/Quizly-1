"""Ollama provider implementation."""

from typing import List, Dict, Any, Optional
import json
import os
import logging
import time
import uuid
import ollama # Ensure ollama is imported

from .base import LLMProvider

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """Ollama provider for local LLM question generation."""

    def __init__(self, model: str = None, host: str = None):
        super().__init__(provider_name="Ollama")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3") # Default to llama3 if not set
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self._client = None
        self._initialize_ollama()

    def _initialize_ollama(self):
        """Initialize Ollama client."""
        try:
            self._client = ollama.Client(host=self.host)
            # Verify connection by listing local models, or a light ping if available
            self._client.list()
            logger.info(f"Ollama provider initialized with model: {self.model} at host: {self.host}")
        except ImportError:
            logger.error("Ollama package not installed. Install with: pip install ollama")
            self._client = None # Ensure client is None
        except Exception as e:
            logger.error(f"Failed to initialize Ollama client or connect to {self.host}: {e}")
            self._client = None # Ensure client is None

    def generate_questions(self, subject: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Generate questions using Ollama."""
        request_id = str(uuid.uuid4())
        target_function = "generate_questions"

        if not self._client:
            self._log_prompt_info(request_id, self.model, target_function, "FAILURE")
            logger.error(f"Ollama client not initialized for host {self.host}. Cannot generate questions.")
            return []

        prompt_text = self._create_prompt(subject, limit)

        api_request_payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt_text}],
            # Ollama specific parameters can be added here if needed, e.g. options
        }

        self._log_prompt_trace_request(
            request_id=request_id, model=self.model, target_function=target_function,
            prompt=prompt_text,
            api_request_details={
                "url": f"{self.host}/api/chat", # Approximate
                "method": "POST",
                "body": api_request_payload
            }
        )

        start_time = time.time()
        raw_response_content: Optional[str] = None
        api_response_data: Dict[str, Any] = {}
        error_message: Optional[str] = None
        status = "FAILURE"

        try:
            response = self._client.chat(**api_request_payload)
            duration_ms = (time.time() - start_time) * 1000

            # Ollama response structure: response['message']['content']
            raw_response_content = response.get("message", {}).get("content")
            api_response_data = response # The whole response dict

            if not raw_response_content:
                error_message = "Ollama response content is empty or not in expected format."
                # Include more response details if available for debugging
                logger.error(f"{error_message} Full response: {response}")
                raise ValueError(error_message)

            parsed_questions = self._parse_response(raw_response_content, subject, limit)
            status = "SUCCESS"

            self._log_prompt_info(request_id, self.model, target_function, status)
            self._log_prompt_debug(request_id, self.model, target_function, status, prompt_text, raw_response_content, duration_ms)
            self._log_prompt_trace_response(request_id, self.model, target_function, status, prompt_text, raw_response_content, duration_ms,
                                            api_request_details={"body": api_request_payload}, api_response_details=api_response_data)
            return parsed_questions

        except (json.JSONDecodeError, ValueError) as e:
            duration_ms = (time.time() - start_time) * 1000
            error_message = f"Failed to parse response from Ollama: {e}. Content: {raw_response_content[:200] if raw_response_content else 'N/A'}..."
            logger.error(f"{error_message} (Request ID: {request_id})")
            self._log_prompt_info(request_id, self.model, target_function, "FAILURE")
            self._log_prompt_debug(request_id, self.model, target_function, "FAILURE", prompt_text, raw_response_content, duration_ms)
            self._log_prompt_trace_response(request_id, self.model, target_function, "FAILURE", prompt_text, raw_response_content, duration_ms,
                                            api_request_details={"body": api_request_payload},
                                            api_response_details=api_response_data or {"error": str(e)},
                                            error_details=error_message)
            raise RuntimeError(error_message)
        except ollama.ResponseError as e: # Specific Ollama client error
            duration_ms = (time.time() - start_time) * 1000
            error_message = f"Ollama API error (status {e.status_code}): {e.error}"
            logger.error(f"{error_message} (Request ID: {request_id})")
            api_response_data = {"status_code": e.status_code, "error": e.error}
            self._log_prompt_info(request_id, self.model, target_function, "FAILURE")
            self._log_prompt_debug(request_id, self.model, target_function, "FAILURE", prompt_text, None, duration_ms)
            self._log_prompt_trace_response(request_id, self.model, target_function, "FAILURE", prompt_text, None, duration_ms,
                                            api_request_details={"body": api_request_payload},
                                            api_response_details=api_response_data,
                                            error_details=error_message)
            raise RuntimeError(f"Ollama API call failed: {e.error}")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            error_message = f"An unexpected error occurred during Ollama call: {e}"
            logger.error(f"{error_message} (Request ID: {request_id})")
            self._log_prompt_info(request_id, self.model, target_function, "FAILURE")
            self._log_prompt_debug(request_id, self.model, target_function, "FAILURE", prompt_text, None, duration_ms)
            self._log_prompt_trace_response(request_id, self.model, target_function, "FAILURE", prompt_text, None, duration_ms,
                                            api_request_details={"body": api_request_payload},
                                            api_response_details=api_response_data or {"error": str(e)},
                                            error_details=error_message)
            raise RuntimeError(f"Ollama question generation failed: {e}")

    def health_check(self) -> bool:
        """Check if Ollama is available."""
        if not self._client:
            logger.warning(f"Ollama health check failed: client not initialized for host {self.host}.")
            return False

        request_id = str(uuid.uuid4())
        target_function = "health_check"
        api_request_payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": "Test connection"}],
            "options": {"num_predict": 1} # Make it a very light request
        }
        self._log_prompt_trace_request(
            request_id=request_id, model=self.model, target_function=target_function,
            prompt="Test connection", api_request_details={"body": api_request_payload}
        )

        start_time = time.time()
        status = "FAILURE"
        error_message: Optional[str] = None
        api_response_data: Dict[str, Any] = {}
        raw_response_content: Optional[str] = None

        try:
            response = self._client.chat(**api_request_payload)
            duration_ms = (time.time() - start_time) * 1000
            api_response_data = response
            raw_response_content = response.get("message", {}).get("content")

            if response and response.get("message") and "content" in response.get("message", {}):
                status = "SUCCESS"
                self._log_prompt_info(request_id, self.model, target_function, status)
                self._log_prompt_debug(request_id, self.model, target_function, status, "Test connection", raw_response_content, duration_ms)
                self._log_prompt_trace_response(request_id, self.model, target_function, status, "Test connection", raw_response_content, duration_ms,
                                                api_request_details={"body": api_request_payload}, api_response_details=api_response_data)
                return True
            else:
                error_message = f"Health check failed: 'message' or 'content' not in response. Response: {response}"
                status = "FAILURE"
        except ollama.ResponseError as e:
            duration_ms = (time.time() - start_time) * 1000
            error_message = f"Ollama health check API error (status {e.status_code}): {e.error}"
            api_response_data = {"status_code": e.status_code, "error": e.error}
            status = "FAILURE"
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            error_message = f"Ollama health check failed with unexpected error: {e}"
            status = "FAILURE"

        logger.warning(f"{error_message or 'Ollama health check failed.'} (Request ID: {request_id})")
        duration_ms_fallback = (time.time() - start_time) * 1000
        self._log_prompt_info(request_id, self.model, target_function, status)
        self._log_prompt_debug(request_id, self.model, target_function, status, "Test connection", raw_response_content, locals().get('duration_ms', duration_ms_fallback))
        self._log_prompt_trace_response(request_id, self.model, target_function, status, "Test connection", raw_response_content, locals().get('duration_ms', duration_ms_fallback),
                                        api_request_details={"body": api_request_payload},
                                        api_response_details=api_response_data or {"error": error_message},
                                        error_details=error_message)
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
