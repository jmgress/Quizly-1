"""Test the new LLM prompt logging functionality."""

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


def test_llm_prompt_logging_config():
    """Test LLM prompt logging configuration."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_config_file = f.name
    
    try:
        # Test with default configuration
        config_mgr = LoggingConfigManager(temp_config_file)
        config = config_mgr.get_config()
        
        # Check that LLM prompt logging is in the configuration
        assert 'llm_prompt_logging' in config
        assert config['llm_prompt_logging']['enabled'] is False
        assert config['llm_prompt_logging']['level'] == 'INFO'
        assert config['llm_prompt_logging']['log_file'] == 'llm_prompts.log'
        
        # Test enabling LLM prompt logging
        update = {
            'llm_prompt_logging': {
                'enabled': True,
                'level': 'DEBUG'
            }
        }
        updated_config = config_mgr.update_config(update)
        
        assert updated_config['llm_prompt_logging']['enabled'] is True
        assert updated_config['llm_prompt_logging']['level'] == 'DEBUG'
        
        # Test the utility methods
        assert config_mgr.is_llm_prompt_logging_enabled() is True
        assert config_mgr.get_llm_prompt_logging_level() == 'DEBUG'
        
        print("LLM prompt logging configuration tests passed!")
        
    finally:
        if os.path.exists(temp_config_file):
            os.remove(temp_config_file)


def test_llm_prompt_logger():
    """Test LLM prompt logger functionality."""
    with tempfile.TemporaryDirectory() as temp_log_dir:
        # Create a proper temp config file with valid JSON
        temp_config_file = os.path.join(temp_log_dir, 'config.json')
        
        try:
            # Create a config manager with enabled LLM logging
            config_mgr = LoggingConfigManager(temp_config_file)
            config_mgr.logs_dir = temp_log_dir
            
            # Enable LLM prompt logging
            config_mgr.update_config({
                'llm_prompt_logging': {
                    'enabled': True,
                    'level': 'DEBUG',
                    'log_file': 'test_llm_prompts.log'
                }
            })
            
            # Test logging a prompt
            config_mgr.log_llm_prompt(
                provider='test_provider',
                model='test_model',
                prompt='Test prompt',
                response='Test response',
                metadata={'test': 'data'},
                timing={'duration_ms': 100},
                level='INFO'
            )
            
            # Check that the log file was created
            log_file_path = os.path.join(temp_log_dir, 'test_llm_prompts.log')
            assert os.path.exists(log_file_path)
            
            # Check the log content
            with open(log_file_path, 'r') as f:
                log_entry = json.loads(f.read().strip())
                assert log_entry['provider'] == 'test_provider'
                assert log_entry['model'] == 'test_model'
                assert log_entry['level'] == 'INFO'
                assert log_entry['status'] == 'success'
                assert 'metadata' in log_entry
                assert 'timing' in log_entry
            
            # Test retrieving logs
            logs = config_mgr.get_llm_prompt_logs()
            assert len(logs) == 1
            assert logs[0]['provider'] == 'test_provider'
            
            print("LLM prompt logger tests passed!")
            
        finally:
            pass  # Temp directory cleanup is automatic


def test_llm_prompt_logger_class():
    """Test LLMPromptLogger class."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_config_file = f.name
    
    with tempfile.TemporaryDirectory() as temp_log_dir:
        try:
            # Mock the config manager
            with patch('llm_prompt_logger.logging_config_manager') as mock_config_mgr:
                mock_config_mgr.is_llm_prompt_logging_enabled.return_value = True
                mock_config_mgr.log_llm_prompt = Mock()
                
                logger = LLMPromptLogger()
                
                # Test direct logging
                logger.log_prompt(
                    provider='test',
                    model='test',
                    prompt='test prompt',
                    response='test response',
                    level='INFO'
                )
                
                # Verify the mock was called
                mock_config_mgr.log_llm_prompt.assert_called_once()
                
                # Test the decorator
                @logger.log_decorator('test_provider', 'test_model')
                def test_function(subject):
                    return f"Generated questions for {subject}"
                
                result = test_function('mathematics')
                assert result == "Generated questions for mathematics"
                
                # Should have been called twice now (once direct, once via decorator)
                assert mock_config_mgr.log_llm_prompt.call_count == 2
                
                print("LLMPromptLogger class tests passed!")
                
        finally:
            if os.path.exists(temp_config_file):
                os.remove(temp_config_file)


if __name__ == "__main__":
    test_llm_prompt_logging_config()
    test_llm_prompt_logger()
    test_llm_prompt_logger_class()
    print("All LLM prompt logging tests passed!")