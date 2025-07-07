"""OpenAI provider implementation."""

from typing import List, Dict, Any, Optional
import json
import os
import logging
import time
import uuid
import openai # Ensure openai is imported if not already

from .base import LLMProvider # Assuming LLMProvider is in .base

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI provider for question generation."""

    def __init__(self, api_key: str = None, model: str = None):
        super().__init__(provider_name="OpenAI") # Call superclass constructor
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._client = None
        self._initialize_openai()

    def _initialize_openai(self):
        """Initialize OpenAI client."""
        if not self.api_key:
            # Log this but don't raise an error, so app can start. Health check will fail.
            logger.warning("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")
            return

        try:
            # Ensure openai is imported before using it
            # import openai # This line might be redundant if already imported at module level
            self._client = openai.OpenAI(api_key=self.api_key)
            logger.info(f"OpenAI provider initialized with model: {self.model}")
        except ImportError:
            logger.error("OpenAI package not installed. Install with: pip install openai")
            # Not raising ImportError to allow app to run, health_check will handle this
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")


    def generate_questions(self, subject: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Generate questions using OpenAI."""
        request_id = str(uuid.uuid4())
        target_function = "generate_questions"

        if not self._client:
            self._log_prompt_info(request_id, self.model, target_function, "FAILURE")
            logger.error("OpenAI client not initialized. Cannot generate questions.")
            # Consider if an empty list or an exception is more appropriate here
            # For now, returning empty list to match potential behavior if API key was missing.
            return []

        prompt_text = self._create_prompt(subject, limit)

        api_request_payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt_text}],
            "temperature": 0.7,
            "max_tokens": 2000,
        }

        self._log_prompt_trace_request(
            request_id=request_id, model=self.model, target_function=target_function,
            prompt=prompt_text,
            api_request_details={
                "url": f"{self._client.base_url}chat/completions", # Approximate
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
            response = self._client.chat.completions.create(**api_request_payload)
            duration_ms = (time.time() - start_time) * 1000

            raw_response_content = response.choices[0].message.content
            api_response_data = response.model_dump() if hasattr(response, 'model_dump') else vars(response)


            if not raw_response_content:
                error_message = "OpenAI response content is empty."
                raise ValueError(error_message)

            parsed_questions = self._parse_response(raw_response_content, subject, limit)
            status = "SUCCESS"

            self._log_prompt_info(request_id, self.model, target_function, status)
            self._log_prompt_debug(request_id, self.model, target_function, status, prompt_text, raw_response_content, duration_ms)
            self._log_prompt_trace_response(request_id, self.model, target_function, status, prompt_text, raw_response_content, duration_ms,
                                            api_request_details={"body": api_request_payload}, api_response_details=api_response_data)
            return parsed_questions

        except (json.JSONDecodeError, ValueError) as e: # Catch parsing errors specifically
            duration_ms = (time.time() - start_time) * 1000
            error_message = f"Failed to parse response from OpenAI: {e}. Content: {raw_response_content[:200] if raw_response_content else 'N/A'}..."
            logger.error(f"{error_message} (Request ID: {request_id})")
            self._log_prompt_info(request_id, self.model, target_function, "FAILURE")
            self._log_prompt_debug(request_id, self.model, target_function, "FAILURE", prompt_text, raw_response_content, duration_ms)
            self._log_prompt_trace_response(request_id, self.model, target_function, "FAILURE", prompt_text, raw_response_content, duration_ms,
                                            api_request_details={"body": api_request_payload},
                                            api_response_details=api_response_data or {"error": str(e)},
                                            error_details=error_message)
            raise RuntimeError(error_message) # Re-raise as a generic runtime error for the caller
        except openai.APIError as e: # More specific OpenAI client error
            duration_ms = (time.time() - start_time) * 1000
            error_message = f"OpenAI API error: {e}"
            logger.error(f"{error_message} (Request ID: {request_id})")
            api_response_data = {"status_code": e.status_code, "error_type": e.type, "message": str(e)} if hasattr(e, 'status_code') else {"error": str(e)}
            self._log_prompt_info(request_id, self.model, target_function, "FAILURE")
            self._log_prompt_debug(request_id, self.model, target_function, "FAILURE", prompt_text, None, duration_ms)
            self._log_prompt_trace_response(request_id, self.model, target_function, "FAILURE", prompt_text, None, duration_ms,
                                            api_request_details={"body": api_request_payload},
                                            api_response_details=api_response_data,
                                            error_details=error_message)
            raise RuntimeError(f"OpenAI API call failed: {e}") # Re-raise
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            error_message = f"An unexpected error occurred during OpenAI call: {e}"
            logger.error(f"{error_message} (Request ID: {request_id})")
            self._log_prompt_info(request_id, self.model, target_function, "FAILURE")
            self._log_prompt_debug(request_id, self.model, target_function, "FAILURE", prompt_text, None, duration_ms)
            self._log_prompt_trace_response(request_id, self.model, target_function, "FAILURE", prompt_text, None, duration_ms,
                                            api_request_details={"body": api_request_payload},
                                            api_response_details=api_response_data or {"error": str(e)},
                                            error_details=error_message)
            raise RuntimeError(f"OpenAI question generation failed: {e}")


    def health_check(self) -> bool:
        """Check if OpenAI API is available."""
        if not self._client:
            logger.warning("OpenAI health check failed: client not initialized.")
            return False

        request_id = str(uuid.uuid4())
        target_function = "health_check"
        api_request_payload = {
            "model": self.model, # Use a small, fast model if possible, or the configured one
            "messages": [{"role": "user", "content": "Test"}],
            "max_tokens": 1,
        }
        self._log_prompt_trace_request(
            request_id=request_id, model=self.model, target_function=target_function,
            prompt="Test", api_request_details={"body": api_request_payload}
        )

        start_time = time.time()
        status = "FAILURE"
        error_message: Optional[str] = None
        api_response_data: Dict[str, Any] = {}

        try:
            response = self._client.chat.completions.create(**api_request_payload)
            duration_ms = (time.time() - start_time) * 1000
            api_response_data = response.model_dump() if hasattr(response, 'model_dump') else vars(response)

            if response.choices[0].message.content is not None:
                status = "SUCCESS"
                self._log_prompt_info(request_id, self.model, target_function, status)
                self._log_prompt_debug(request_id, self.model, target_function, status, "Test", response.choices[0].message.content, duration_ms)
                self._log_prompt_trace_response(request_id, self.model, target_function, status, "Test", response.choices[0].message.content, duration_ms,
                                                api_request_details={"body": api_request_payload}, api_response_details=api_response_data)
                return True
            else:
                error_message = "Health check failed: No content in response."
                status = "FAILURE"
        except openai.APIError as e: # More specific OpenAI client error
            duration_ms = (time.time() - start_time) * 1000
            error_message = f"OpenAI health check API error: {e}"
            api_response_data = {"status_code": e.status_code, "error_type": e.type, "message": str(e)} if hasattr(e, 'status_code') else {"error": str(e)}
            status = "FAILURE"
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            error_message = f"OpenAI health check failed with unexpected error: {e}"
            status = "FAILURE"

        # Log failure if any exception occurred or if status is FAILURE
        logger.warning(f"{error_message or 'OpenAI health check failed.'} (Request ID: {request_id})")
        duration_ms_fallback = (time.time() - start_time) * 1000 # Recalculate if not set
        self._log_prompt_info(request_id, self.model, target_function, status)
        self._log_prompt_debug(request_id, self.model, target_function, status, "Test", None, locals().get('duration_ms', duration_ms_fallback))
        self._log_prompt_trace_response(request_id, self.model, target_function, status, "Test", None, locals().get('duration_ms', duration_ms_fallback),
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
