"""Base definitions for LLM providers."""

import logging
import time
import uuid
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional

from backend.logging_config import logging_config_manager

# Dedicated logger for LLM prompts
llm_prompt_logger = logging.getLogger("backend.llm_prompts")
# Prevent llm_prompt_logger from propagating to the root logger
# if we want separate handling, but for now, let it use root handlers
# llm_prompt_logger.propagate = False
# We'll rely on the main logging setup to configure handlers for backend.* loggers

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.config_manager = logging_config_manager

    def _log_prompt_info(self, request_id: str, model: str, target_function: str, status: str):
        """Logs basic prompt metadata (INFO level)."""
        llm_config = self.config_manager.get_llm_prompt_logging_config()
        if not llm_config.get("enabled"):
            return

        current_level_idx = ["INFO", "DEBUG", "TRACE"].index(llm_config.get("level", "INFO").upper())
        if current_level_idx >= ["INFO", "DEBUG", "TRACE"].index("INFO"):
            log_entry = {
                "request_id": request_id,
                "llm_event_type": "LLM_PROMPT_RESPONSE", # Assuming this is logged after response
                "provider": self.provider_name,
                "model": model,
                "target_function": target_function,
                "status": status,
            }
            llm_prompt_logger.info(json.dumps(log_entry))

    def _log_prompt_debug(self, request_id: str, model: str, target_function: str, status: str,
                          prompt: str, response: Optional[str], duration_ms: float):
        """Logs full prompts and responses with timing (DEBUG level)."""
        llm_config = self.config_manager.get_llm_prompt_logging_config()
        if not llm_config.get("enabled"):
            return

        current_level_idx = ["INFO", "DEBUG", "TRACE"].index(llm_config.get("level", "INFO").upper())
        if current_level_idx >= ["INFO", "DEBUG", "TRACE"].index("DEBUG"):
            log_entry = {
                "request_id": request_id,
                "llm_event_type": "LLM_PROMPT_RESPONSE",
                "provider": self.provider_name,
                "model": model,
                "target_function": target_function,
                "status": status,
                "prompt": prompt,
                "response": response,
                "duration_ms": round(duration_ms, 2),
            }
            llm_prompt_logger.debug(json.dumps(log_entry))

    def _log_prompt_trace_request(self, request_id: str, model: str, target_function: str,
                                  prompt: str, api_request_details: Dict[str, Any]):
        """Logs complete request cycle details (TRACE level)."""
        llm_config = self.config_manager.get_llm_prompt_logging_config()
        if not llm_config.get("enabled"):
            return

        current_level_idx = ["INFO", "DEBUG", "TRACE"].index(llm_config.get("level", "INFO").upper())
        if current_level_idx >= ["INFO", "DEBUG", "TRACE"].index("TRACE"):
            log_entry = {
                "request_id": request_id,
                "llm_event_type": "LLM_PROMPT_REQUEST",
                "provider": self.provider_name,
                "model": model,
                "target_function": target_function,
                "prompt": prompt,
                "api_request": api_request_details,
            }
            llm_prompt_logger.debug(json.dumps(log_entry)) # TRACE is logged as DEBUG with more data

    def _log_prompt_trace_response(self, request_id: str, model: str, target_function: str, status: str,
                                   prompt: str, response: Optional[str], duration_ms: float,
                                   api_request_details: Dict[str, Any],
                                   api_response_details: Dict[str, Any],
                                   error_details: Optional[str] = None):
        """Logs complete response cycle details (TRACE level)."""
        llm_config = self.config_manager.get_llm_prompt_logging_config()
        if not llm_config.get("enabled"):
            return

        current_level_idx = ["INFO", "DEBUG", "TRACE"].index(llm_config.get("level", "INFO").upper())
        if current_level_idx >= ["INFO", "DEBUG", "TRACE"].index("TRACE"):
            log_entry = {
                "request_id": request_id,
                "llm_event_type": "LLM_API_ERROR" if status == "FAILURE" else "LLM_PROMPT_RESPONSE",
                "provider": self.provider_name,
                "model": model,
                "target_function": target_function,
                "status": status,
                "prompt": prompt,
                "response": response,
                "duration_ms": round(duration_ms, 2),
                "api_request": api_request_details,
                "api_response": api_response_details,
            }
            if error_details:
                log_entry["error_details"] = error_details
            # TRACE is logged as DEBUG with more data. If a dedicated TRACE level is configured
            # in Python's logging, this could be llm_prompt_logger.trace()
            llm_prompt_logger.debug(json.dumps(log_entry))


    @abstractmethod
    def generate_questions(self, subject: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Generate quiz questions for a given subject."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if the provider is available and working."""
        pass
