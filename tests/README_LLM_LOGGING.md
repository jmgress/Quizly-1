# LLM Logging Tests

## Overview
The `test_llm_logging.py` file contains comprehensive tests for the LLM logging functionality in the Quizly application.

## Test Coverage

### 1. Configuration Tests
- **test_llm_logging_configuration**: Verifies that LLM logging is properly configured and enabled
- **test_logging_when_disabled**: Ensures no logging occurs when LLM logging is disabled

### 2. Basic Functionality Tests
- **test_log_llm_prompt_basic**: Tests basic LLM prompt logging with successful responses
- **test_log_llm_prompt_with_error**: Tests LLM prompt logging with error responses
- **test_log_llm_prompt_level_filtering**: Verifies that log level filtering works correctly

### 3. Data Retrieval Tests
- **test_get_llm_prompt_logs**: Tests retrieving and parsing logged LLM interactions

## What Gets Logged

The LLM logging system captures:
- **Provider**: Which LLM provider was used (OpenAI, Ollama, etc.)
- **Model**: The specific model used
- **Prompt**: The full prompt sent to the LLM
- **Response**: The response from the LLM (preview or full based on config)
- **Metadata**: Additional information like subject, question count, etc.
- **Timing**: Duration of the LLM call in milliseconds
- **Status**: Success or error status
- **Error details**: If the call failed, error information is logged

## Configuration

The tests verify that the logging configuration in `logging_config.json` is properly loaded and applied:

```json
{
  "llm_prompt_logging": {
    "enabled": true,
    "level": "DEBUG",
    "log_file": "backend/llm_prompts.log",
    "include_metadata": true,
    "include_timing": true,
    "include_full_response": true
  }
}
```

## Running the Tests

The tests can be run in several ways:

1. **Directly**: `python3 tests/test_llm_logging.py`
2. **Via test suite**: `./run_tests.sh` (includes these tests as "Test 4: LLM Logging Tests")
3. **Via pytest**: `pytest tests/test_llm_logging.py -v`

## Integration with Test Suite

The LLM logging tests are integrated into the main test suite (`run_tests.sh`) and will be automatically executed as part of the backend test suite.

## Test Files and Cleanup

The tests create temporary log files during execution and clean them up afterward to avoid interference between test runs.
