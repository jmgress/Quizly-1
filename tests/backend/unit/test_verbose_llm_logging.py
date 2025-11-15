"""Test verbose LLM logging functionality."""

import tempfile
import os
import json
import pytest
from unittest.mock import Mock, patch

# Add the backend directory to the path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from logging_config import LoggingConfigManager
from llm_prompt_logger import LLMPromptLogger


def test_verbose_logging_config():
    """Test verbose logging configuration."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_config_file = f.name
    
    try:
        # Test with default configuration
        config_mgr = LoggingConfigManager(temp_config_file)
        config = config_mgr.get_config()
        
        # Check that verbose logging is in the configuration
        assert 'llm_verbose_logging' in config
        assert config['llm_verbose_logging']['enabled'] is False
        assert config['llm_verbose_logging']['level'] == 'detailed'
        assert config['llm_verbose_logging']['log_file'] == 'backend/llm_prompts_verbose.log'
        assert config['llm_verbose_logging']['sanitize_api_keys'] is True
        
        # Test enabling verbose logging
        update = {
            'llm_verbose_logging': {
                'enabled': True,
                'level': 'full',
                'providers': ['ollama']
            }
        }
        updated_config = config_mgr.update_config(update)
        
        assert updated_config['llm_verbose_logging']['enabled'] is True
        assert updated_config['llm_verbose_logging']['level'] == 'full'
        assert 'ollama' in updated_config['llm_verbose_logging']['providers']
        
        # Test the utility methods
        assert config_mgr.is_verbose_logging_enabled() is True
        assert config_mgr.get_verbose_logging_level() == 'full'
        assert 'ollama' in config_mgr.get_verbose_logging_providers()
        
        print("Verbose logging configuration tests passed!")
        
    finally:
        if os.path.exists(temp_config_file):
            os.remove(temp_config_file)


def test_verbose_logging_basic_level():
    """Test verbose logging at basic level."""
    with tempfile.TemporaryDirectory() as temp_log_dir:
        temp_config_file = os.path.join(temp_log_dir, 'config.json')
        
        config_mgr = LoggingConfigManager(temp_config_file)
        config_mgr.logs_dir = temp_log_dir
        
        # Enable verbose logging at basic level
        config_mgr.update_config({
            'llm_verbose_logging': {
                'enabled': True,
                'level': 'basic',
                'log_file': 'test_verbose.log',
                'providers': ['test_provider']
            }
        })
        
        # Log a verbose interaction
        config_mgr.log_verbose_llm_interaction(
            provider='test_provider',
            model='test_model',
            prompt='This is a test prompt that is quite long',
            response='This is a test response',
            metadata={'test': 'data'},
            timing={'duration_ms': 100},
            request_id='test-123'
        )
        
        # Check that the log file was created
        log_file_path = os.path.join(temp_log_dir, 'test_verbose.log')
        assert os.path.exists(log_file_path)
        
        # Check the log content
        with open(log_file_path, 'r') as f:
            log_entry = json.loads(f.read().strip())
            assert log_entry['provider'] == 'test_provider'
            assert log_entry['model'] == 'test_model'
            assert log_entry['request_id'] == 'test-123'
            assert log_entry['status'] == 'success'
            # At basic level, should have lengths not full content
            assert 'prompt_length' in log_entry
            assert 'response_length' in log_entry
            assert 'prompt' not in log_entry
            assert 'response' not in log_entry
        
        print("Basic level verbose logging tests passed!")


def test_verbose_logging_detailed_level():
    """Test verbose logging at detailed level."""
    with tempfile.TemporaryDirectory() as temp_log_dir:
        temp_config_file = os.path.join(temp_log_dir, 'config.json')
        
        config_mgr = LoggingConfigManager(temp_config_file)
        config_mgr.logs_dir = temp_log_dir
        
        # Enable verbose logging at detailed level
        config_mgr.update_config({
            'llm_verbose_logging': {
                'enabled': True,
                'level': 'detailed',
                'log_file': 'test_verbose.log',
                'providers': ['test_provider'],
                'include_responses': True,
                'include_metadata': True
            }
        })
        
        # Log a verbose interaction
        test_prompt = 'This is a test prompt'
        test_response = 'This is a test response'
        config_mgr.log_verbose_llm_interaction(
            provider='test_provider',
            model='test_model',
            prompt=test_prompt,
            response=test_response,
            metadata={'subject': 'math', 'limit': 5},
            timing={'duration_ms': 150},
            request_id='test-456',
            status_code=200
        )
        
        # Check the log content
        log_file_path = os.path.join(temp_log_dir, 'test_verbose.log')
        with open(log_file_path, 'r') as f:
            log_entry = json.loads(f.read().strip())
            assert log_entry['provider'] == 'test_provider'
            assert log_entry['request_id'] == 'test-456'
            assert log_entry['status_code'] == 200
            # At detailed level, should have truncated content
            assert 'prompt' in log_entry
            assert 'response' in log_entry
            assert log_entry['prompt'] == test_prompt  # Short enough to not be truncated
            assert log_entry['response'] == test_response
            assert log_entry['metadata']['subject'] == 'math'
            assert log_entry['timing']['duration_ms'] == 150
        
        print("Detailed level verbose logging tests passed!")


def test_verbose_logging_full_level():
    """Test verbose logging at full level."""
    with tempfile.TemporaryDirectory() as temp_log_dir:
        temp_config_file = os.path.join(temp_log_dir, 'config.json')
        
        config_mgr = LoggingConfigManager(temp_config_file)
        config_mgr.logs_dir = temp_log_dir
        
        # Enable verbose logging at full level
        config_mgr.update_config({
            'llm_verbose_logging': {
                'enabled': True,
                'level': 'full',
                'log_file': 'test_verbose.log',
                'providers': ['test_provider'],
                'include_responses': True
            }
        })
        
        # Log with long content
        long_prompt = 'A' * 2000  # Long prompt
        long_response = 'B' * 2000  # Long response
        
        config_mgr.log_verbose_llm_interaction(
            provider='test_provider',
            model='test_model',
            prompt=long_prompt,
            response=long_response,
            request_id='test-789'
        )
        
        # Check the log content
        log_file_path = os.path.join(temp_log_dir, 'test_verbose.log')
        with open(log_file_path, 'r') as f:
            log_entry = json.loads(f.read().strip())
            # At full level, should have complete content
            assert 'prompt_full' in log_entry
            assert 'response_full' in log_entry
            assert len(log_entry['prompt_full']) == 2000
            assert len(log_entry['response_full']) == 2000
        
        print("Full level verbose logging tests passed!")


def test_sanitize_api_keys():
    """Test that API keys are sanitized in logs."""
    with tempfile.TemporaryDirectory() as temp_log_dir:
        temp_config_file = os.path.join(temp_log_dir, 'config.json')
        
        config_mgr = LoggingConfigManager(temp_config_file)
        config_mgr.logs_dir = temp_log_dir
        
        # Enable verbose logging with sanitization
        config_mgr.update_config({
            'llm_verbose_logging': {
                'enabled': True,
                'level': 'detailed',
                'log_file': 'test_verbose.log',
                'providers': ['openai'],
                'sanitize_api_keys': True
            }
        })
        
        # Log with API key in prompt
        prompt_with_key = 'Use this API key: sk-1234567890abcdefghij to access the service'
        
        config_mgr.log_verbose_llm_interaction(
            provider='openai',
            model='gpt-4',
            prompt=prompt_with_key,
            response='Response',
            request_id='test-sanitize'
        )
        
        # Check that API key is sanitized
        log_file_path = os.path.join(temp_log_dir, 'test_verbose.log')
        with open(log_file_path, 'r') as f:
            log_entry = json.loads(f.read().strip())
            assert 'sk-1234567890abcdefghij' not in log_entry['prompt']
            assert '[API_KEY_REDACTED]' in log_entry['prompt']
        
        print("API key sanitization tests passed!")


def test_provider_filtering():
    """Test that verbose logging respects provider filtering."""
    with tempfile.TemporaryDirectory() as temp_log_dir:
        temp_config_file = os.path.join(temp_log_dir, 'config.json')
        
        config_mgr = LoggingConfigManager(temp_config_file)
        config_mgr.logs_dir = temp_log_dir
        
        # Enable verbose logging only for ollama
        config_mgr.update_config({
            'llm_verbose_logging': {
                'enabled': True,
                'level': 'detailed',
                'log_file': 'test_verbose.log',
                'providers': ['ollama']  # Only ollama
            }
        })
        
        # Log from ollama (should be logged)
        config_mgr.log_verbose_llm_interaction(
            provider='ollama',
            model='llama3.2',
            prompt='Ollama prompt',
            response='Ollama response'
        )
        
        # Log from openai (should NOT be logged)
        config_mgr.log_verbose_llm_interaction(
            provider='openai',
            model='gpt-4',
            prompt='OpenAI prompt',
            response='OpenAI response'
        )
        
        # Check that only ollama was logged
        log_file_path = os.path.join(temp_log_dir, 'test_verbose.log')
        with open(log_file_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 1  # Only one entry
            log_entry = json.loads(lines[0])
            assert log_entry['provider'] == 'ollama'
        
        print("Provider filtering tests passed!")


def test_verbose_log_retrieval_with_provider_filter():
    """Test retrieving verbose logs with provider filter."""
    with tempfile.TemporaryDirectory() as temp_log_dir:
        temp_config_file = os.path.join(temp_log_dir, 'config.json')
        
        config_mgr = LoggingConfigManager(temp_config_file)
        config_mgr.logs_dir = temp_log_dir
        
        # Enable verbose logging for both providers
        config_mgr.update_config({
            'llm_verbose_logging': {
                'enabled': True,
                'level': 'detailed',
                'log_file': 'test_verbose.log',
                'providers': ['ollama', 'openai']
            }
        })
        
        # Log from both providers
        config_mgr.log_verbose_llm_interaction(
            provider='ollama',
            model='llama3.2',
            prompt='Ollama prompt',
            response='Ollama response'
        )
        
        config_mgr.log_verbose_llm_interaction(
            provider='openai',
            model='gpt-4',
            prompt='OpenAI prompt',
            response='OpenAI response'
        )
        
        # Get all logs
        all_logs = config_mgr.get_verbose_llm_logs()
        assert len(all_logs) == 2
        
        # Get only ollama logs
        ollama_logs = config_mgr.get_verbose_llm_logs(provider='ollama')
        assert len(ollama_logs) == 1
        assert ollama_logs[0]['provider'] == 'ollama'
        
        # Get only openai logs
        openai_logs = config_mgr.get_verbose_llm_logs(provider='openai')
        assert len(openai_logs) == 1
        assert openai_logs[0]['provider'] == 'openai'
        
        print("Verbose log retrieval with provider filter tests passed!")


if __name__ == "__main__":
    test_verbose_logging_config()
    test_verbose_logging_basic_level()
    test_verbose_logging_detailed_level()
    test_verbose_logging_full_level()
    test_sanitize_api_keys()
    test_provider_filtering()
    test_verbose_log_retrieval_with_provider_filter()
    print("\n✅ All verbose LLM logging tests passed!")
