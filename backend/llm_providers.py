"""
LLM Provider abstraction layer for question generation.
Supports multiple providers (Ollama, OpenAI) with a common interface.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        
        # Create the prompt template
        prompt = self._create_prompt(subject, limit)
        
        try:
            # Call Ollama API
            response = self._ollama.chat(
                model=self.model,
                messages=[{
                    'role': 'user', 
                    'content': prompt
                }]
            )
            
            # Parse and validate response
            return self._parse_response(response['message']['content'], subject, limit)
            
        except Exception as e:
            logger.error(f"Ollama API call failed: {str(e)}")
            raise RuntimeError(f"Ollama question generation failed: {str(e)}")
    
    def health_check(self) -> bool:
        """Check if Ollama is available."""
        if not self._ollama:
            return False
        
        try:
            # Try a simple request to check connectivity
            response = self._ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': 'Test connection'}]
            )
            return 'message' in response
        except Exception as e:
            logger.warning(f"Ollama health check failed: {str(e)}")
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
        """Parse and validate the response from Ollama."""
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


class OpenAIProvider(LLMProvider):
    """OpenAI provider for question generation."""
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
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


# Provider Factory
def create_llm_provider(provider_type: str = None, **kwargs) -> LLMProvider:
    """
    Factory function to create LLM provider instances.
    
    Args:
        provider_type: Type of provider ("ollama" or "openai")
        **kwargs: Additional configuration for the provider
        
    Returns:
        LLMProvider instance
    """
    if provider_type is None:
        provider_type = os.getenv("LLM_PROVIDER", "ollama").lower()
    
    logger.info(f"Creating LLM provider: {provider_type}")
    
    if provider_type == "ollama":
        model = kwargs.get("model", os.getenv("OLLAMA_MODEL", "llama3.2"))
        host = kwargs.get("host", os.getenv("OLLAMA_HOST", "http://localhost:11434"))
        return OllamaProvider(model=model, host=host)
    
    elif provider_type == "openai":
        api_key = kwargs.get("api_key", os.getenv("OPENAI_API_KEY"))
        model = kwargs.get("model", os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"))
        return OpenAIProvider(api_key=api_key, model=model)
    
    else:
        raise ValueError(f"Unknown provider type: {provider_type}. Supported types: 'ollama', 'openai'")


def get_available_providers() -> List[str]:
    """Get list of available providers based on configuration."""
    providers = []
    
    # Check Ollama
    try:
        provider = create_llm_provider("ollama")
        if provider.health_check():
            providers.append("ollama")
    except Exception:
        pass
    
    # Check OpenAI
    try:
        if os.getenv("OPENAI_API_KEY"):
            provider = create_llm_provider("openai")
            if provider.health_check():
                providers.append("openai")
    except Exception:
        pass
    
    return providers