import abc
import json
import os
import logging
import requests # For OllamaProvider
# We'll need openai library later, good to import it if available or add to requirements
try:
    import openai
except ImportError:
    # This is fine for now, OpenAIProvider will raise an error if used without the library
    pass

logger = logging.getLogger(__name__)

class LLMProvider(abc.ABC):
    """Abstract base class for LLM providers."""

    @abc.abstractmethod
    def generate_questions(self, subject: str, limit: int) -> list[dict]:
        """
        Generates quiz questions for a given subject.

        Args:
            subject: The subject for which to generate questions.
            limit: The maximum number of questions to generate.

        Returns:
            A list of dictionaries, where each dictionary represents a question
            in the format expected by the frontend/database.
            Example:
            {
                "text": "question text here?",
                "options": [
                    {"id": "a", "text": "option A text"},
                    {"id": "b", "text": "option B text"},
                    {"id": "c", "text": "option C text"},
                    {"id": "d", "text": "option D text"}
                ],
                "correct_answer": "a", // or "b", "c", "d"
                "category": "subject" // lowercase subject
            }
        """
        pass

class OllamaProvider(LLMProvider):
    """LLM provider for Ollama."""

    def __init__(self, host: str = "http://localhost:11434", model: str = "llama3.2"): # Changed default model
        self.host = host
        self.model = model
        # The prompt template will be passed from the environment or a config
        self.prompt_template = os.getenv(
            "PROMPT_TEMPLATE",
            """Generate {limit} multiple-choice quiz questions about {subject}.
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
    "category": "{subject_lowercase}"
}}

Return only the JSON array, no additional text."""
        )

    def generate_questions(self, subject: str, limit: int) -> list[dict]:
        prompt = self.prompt_template.format(limit=limit, subject=subject, subject_lowercase=subject.lower())

        try:
            # Using requests library for Ollama, similar to how ollama.chat might work
            # The official ollama library uses httpx, but requests is also common.
            # Sticking to ollama library for consistency with existing code in main.py
            # For now, let's assume `ollama` library is available as it was in main.py
            import ollama as ollama_client # Renaming to avoid conflict if we had a local ollama.py

            response = ollama_client.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                # host can be configured if ollama client supports it, or via OLLAMA_HOST env var
                # For now, assuming default host or OLLAMA_HOST is picked up by the client
            )

            content = response['message']['content']

            try:
                questions_data = json.loads(content)
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON directly. Attempting to extract from string.")
                # Attempt to extract JSON array from potentially messy string
                start_index = content.find('[')
                end_index = content.rfind(']') + 1
                if start_index != -1 and end_index != -1 and end_index > start_index:
                    json_str = content[start_index:end_index]
                    questions_data = json.loads(json_str)
                else:
                    logger.error(f"Could not extract JSON from Ollama response: {content}")
                    raise ValueError("Could not parse AI response as JSON")

            if not isinstance(questions_data, list):
                questions_data = [questions_data] # Handle cases where a single object is returned

            parsed_questions = []
            for i, q_data in enumerate(questions_data[:limit]):
                if not all(key in q_data for key in ['text', 'options', 'correct_answer']):
                    logger.warning(f"Skipping malformed question data: {q_data}")
                    continue

                # Validate options
                if not isinstance(q_data.get("options"), list) or len(q_data["options"]) != 4:
                    logger.warning(f"Skipping question with invalid options: {q_data}")
                    continue

                option_ids = [opt.get("id") for opt in q_data["options"]]
                if len(set(option_ids)) != 4 or not all(id_val in ['a', 'b', 'c', 'd'] for id_val in option_ids):
                    logger.warning(f"Skipping question with invalid option IDs: {q_data}")
                    continue

                if q_data.get("correct_answer") not in option_ids:
                    logger.warning(f"Skipping question with invalid correct_answer: {q_data}")
                    continue

                parsed_questions.append({
                    # id will be assigned by the calling function if needed (e.g. temporary IDs)
                    "text": q_data["text"],
                    "options": q_data["options"],
                    "correct_answer": q_data["correct_answer"],
                    "category": q_data.get("category", subject.lower()) # Use category from LLM or default
                })

            if not parsed_questions:
                 logger.error(f"No valid questions could be parsed from Ollama response for subject '{subject}'. Response content: {content}")
                 # Consider raising an error or returning empty list based on desired strictness
                 # For now, returning empty and logging, can be made stricter.
                 return []

            return parsed_questions

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Ollama connection error: {e}")
            raise LLMConnectionError(f"Could not connect to Ollama at {self.host}. Ensure Ollama is running.") from e
        except ollama_client.ResponseError as e: # Catching specific ollama client errors
            logger.error(f"Ollama API error: {e.status_code} - {e.error}")
            raise LLMAPIError(f"Ollama API error: {e.error}") from e
        except Exception as e:
            logger.error(f"Error generating questions with Ollama: {e}")
            # Re-raise as a more generic custom error if desired, or let it propagate
            # For now, let it propagate to be caught by the main AI generation function
            raise

class OpenAIProvider(LLMProvider):
    """LLM provider for OpenAI."""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        if not api_key:
            raise ValueError("OpenAI API key is required.")
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
        except ImportError:
            logger.error("OpenAI Python client library not found. Please install it: pip install openai")
            raise ImportError("OpenAI Python client library not found. Please install it: pip install openai")

        self.model = model
        self.prompt_template = os.getenv(
            "PROMPT_TEMPLATE",  # Using the same env var for prompt template
            """Generate {limit} multiple-choice quiz questions about {subject}.
Each question should have exactly 4 answer options labeled a, b, c, d.
Format your response as a JSON object containing a single key "questions" which is an array of question objects.
Each question object should have this structure:
{{
    "text": "question text here?",
    "options": [
        {{"id": "a", "text": "option A text"}},
        {{"id": "b", "text": "option B text"}},
        {{"id": "c", "text": "option C text"}},
        {{"id": "d", "text": "option D text"}}
    ],
    "correct_answer": "a",
    "category": "{subject_lowercase}"
}}

Return only the JSON object, no additional text.
Example for one question about 'Python':
{{
  "questions": [
    {{
      "text": "What is the primary use of the 'self' keyword in Python class methods?",
      "options": [
        {{"id": "a", "text": "To declare a variable static"}},
        {{"id": "b", "text": "To refer to the instance of the class"}},
        {{"id": "c", "text": "To create a private method"}},
        {{"id": "d", "text": "To define a class constructor"}}
      ],
      "correct_answer": "b",
      "category": "python"
    }}
  ]
}}
"""
        )


    def generate_questions(self, subject: str, limit: int) -> list[dict]:
        prompt = self.prompt_template.format(limit=limit, subject=subject, subject_lowercase=subject.lower())

        try:
            import openai # Ensure it's imported here too

            # For OpenAI, it's better to use the dedicated "json_mode" if available
            # This requires the model to be updated (e.g. gpt-3.5-turbo-1106 or later)
            # and the prompt to instruct JSON output.
            chat_completion = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"}, # Enable JSON mode
                messages=[
                    {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                    {"role": "user", "content": prompt}
                ]
            )

            response_content = chat_completion.choices[0].message.content
            if response_content is None:
                logger.error("OpenAI returned an empty response.")
                raise ValueError("OpenAI returned an empty response.")

            try:
                # The prompt asks for {"questions": [...]}, so we extract that.
                data = json.loads(response_content)
                questions_data = data.get("questions", [])
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response from OpenAI: {response_content}. Error: {e}")
                raise ValueError("Could not parse AI response from OpenAI as JSON.")

            if not isinstance(questions_data, list):
                logger.warning(f"OpenAI response 'questions' field was not a list: {questions_data}")
                # Attempt to wrap if it's a single dictionary, though the prompt is specific
                if isinstance(questions_data, dict):
                    questions_data = [questions_data]
                else:
                    questions_data = [] # Or raise error

            parsed_questions = []
            for i, q_data in enumerate(questions_data[:limit]):
                if not all(key in q_data for key in ['text', 'options', 'correct_answer']):
                    logger.warning(f"Skipping malformed question data from OpenAI: {q_data}")
                    continue

                if not isinstance(q_data.get("options"), list) or len(q_data["options"]) != 4:
                    logger.warning(f"Skipping question with invalid options from OpenAI: {q_data}")
                    continue

                option_ids = [opt.get("id") for opt in q_data["options"]]
                if len(set(option_ids)) != 4 or not all(id_val in ['a', 'b', 'c', 'd'] for id_val in option_ids):
                    logger.warning(f"Skipping question with invalid option IDs from OpenAI: {q_data}")
                    continue

                if q_data.get("correct_answer") not in option_ids:
                    logger.warning(f"Skipping question with invalid correct_answer from OpenAI: {q_data}")
                    continue

                parsed_questions.append({
                    "text": q_data["text"],
                    "options": q_data["options"],
                    "correct_answer": q_data["correct_answer"],
                    "category": q_data.get("category", subject.lower())
                })

            if not parsed_questions:
                 logger.error(f"No valid questions could be parsed from OpenAI response for subject '{subject}'. Response content: {response_content}")
                 return [] # Or raise error

            return parsed_questions

        except openai.APIConnectionError as e:
            logger.error(f"OpenAI API connection error: {e}")
            raise LLMConnectionError(f"Could not connect to OpenAI API. {e}") from e
        except openai.RateLimitError as e:
            logger.error(f"OpenAI API request exceeded rate limit: {e}")
            raise LLMAPIError(f"OpenAI rate limit exceeded. {e}") from e
        except openai.APIStatusError as e:
            logger.error(f"OpenAI API returned an error status: {e.status_code} - {e.response}")
            raise LLMAPIError(f"OpenAI API error: {e.status_code} - {e.message}") from e
        except Exception as e:
            logger.error(f"Error generating questions with OpenAI: {e}")
            raise # Re-raise for now


# Custom exceptions for providers
class LLMProviderError(Exception):
    """Base class for provider-related errors."""
    pass

class LLMConnectionError(LLMProviderError):
    """Raised when a provider cannot connect to the LLM service."""
    pass

class LLMAPIError(LLMProviderError):
    """Raised when the LLM service API returns an error."""
    pass

# Factory function will be added here in a later step.
def get_llm_provider() -> LLMProvider:
    """
    Factory function to get the configured LLM provider.
    Reads configuration from environment variables.
    """
    provider_name = os.getenv("LLM_PROVIDER", "ollama").lower()
    logger.info(f"Attempting to initialize LLM provider: {provider_name}")

    if provider_name == "ollama":
        host = os.getenv("OLLAMA_API_HOST", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "llama3.2") # Changed default model
        logger.info(f"Using OllamaProvider with host: {host}, model: {model}")
        return OllamaProvider(host=host, model=model)

    elif provider_name == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OpenAI provider selected, but OPENAI_API_KEY is not set.")
            raise ValueError("OPENAI_API_KEY is required for OpenAIProvider but not found in environment variables.")
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        logger.info(f"Using OpenAIProvider with model: {model}")
        return OpenAIProvider(api_key=api_key, model=model)

    else:
        logger.warning(
            f"Invalid LLM_PROVIDER '{provider_name}' specified. "
            f"Defaulting to OllamaProvider. Supported providers are 'ollama', 'openai'."
        )
        # Default to Ollama with its defaults if provider name is unknown
        host = os.getenv("OLLAMA_API_HOST", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "llama3.2") # Changed default model
        return OllamaProvider(host=host, model=model)

# Example usage (for testing purposes, will be removed or moved to tests)
if __name__ == '__main__':
    # This basic test won't run without Ollama running or OpenAI API key
    # print("Testing OllamaProvider (requires Ollama running with 'mistral' model)...")
    # try:
    #     ollama_provider = OllamaProvider(model="mistral")
    #     questions = ollama_provider.generate_questions("Python programming", 2)
    #     print("Ollama generated questions:")
    #     for q in questions:
    #         print(json.dumps(q, indent=2))
    # except Exception as e:
    #     print(f"Error testing OllamaProvider: {e}")

    # print("\nTesting OpenAIProvider (requires OPENAI_API_KEY env var)...")
    # openai_api_key = os.getenv("OPENAI_API_KEY")
    # if openai_api_key:
    #     try:
    #         openai_provider = OpenAIProvider(api_key=openai_api_key, model="gpt-3.5-turbo")
    #         questions = openai_provider.generate_questions("Quantum Physics", 1)
    #         print("OpenAI generated questions:")
    #         for q in questions:
    #             print(json.dumps(q, indent=2))
    #     except Exception as e:
    #         print(f"Error testing OpenAIProvider: {e}")
    # else:
    #     print("OPENAI_API_KEY not set, skipping OpenAIProvider test.")
    pass
