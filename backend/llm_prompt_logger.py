"""LLM Prompt Logger for tracking LLM interactions."""

import time
import logging
from typing import Dict, Any, Optional, Callable
from functools import wraps
from logging_config import logging_config_manager

logger = logging.getLogger(__name__)


class LLMPromptLogger:
    """Logger specifically for LLM prompts and responses."""
    
    def __init__(self):
        self.config_manager = logging_config_manager
    
    def log_prompt(self, provider: str, model: str, prompt: str, response: str = None,
                   metadata: Dict[str, Any] = None, timing: Dict[str, Any] = None,
                   error: str = None, level: str = "INFO"):
        """Log an LLM prompt interaction."""
        self.config_manager.log_llm_prompt(
            provider=provider,
            model=model,
            prompt=prompt,
            response=response,
            metadata=metadata,
            timing=timing,
            error=error,
            level=level
        )
    
    def log_decorator(self, provider: str, model: str):
        """Decorator to automatically log LLM function calls."""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.config_manager.is_llm_prompt_logging_enabled():
                    return func(*args, **kwargs)
                
                start_time = time.time()
                
                # Extract prompt from arguments
                prompt = ""
                if args:
                    prompt = str(args[0]) if args else ""
                elif 'prompt' in kwargs:
                    prompt = str(kwargs['prompt'])
                elif 'subject' in kwargs:
                    prompt = f"Generate questions for: {kwargs['subject']}"
                
                metadata = {
                    "function": func.__name__,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys())
                }
                
                try:
                    result = func(*args, **kwargs)
                    end_time = time.time()
                    
                    timing = {
                        "start_time": start_time,
                        "end_time": end_time,
                        "duration_ms": round((end_time - start_time) * 1000, 2)
                    }
                    
                    # Log successful interaction
                    self.log_prompt(
                        provider=provider,
                        model=model,
                        prompt=prompt,
                        response=str(result)[:1000] if result else None,
                        metadata=metadata,
                        timing=timing,
                        level="INFO"
                    )
                    
                    return result
                    
                except Exception as e:
                    end_time = time.time()
                    
                    timing = {
                        "start_time": start_time,
                        "end_time": end_time,
                        "duration_ms": round((end_time - start_time) * 1000, 2)
                    }
                    
                    # Log failed interaction
                    self.log_prompt(
                        provider=provider,
                        model=model,
                        prompt=prompt,
                        metadata=metadata,
                        timing=timing,
                        error=str(e),
                        level="ERROR"
                    )
                    
                    raise
            
            return wrapper
        return decorator


# Global instance
llm_prompt_logger = LLMPromptLogger()