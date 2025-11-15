# Verbose LLM Logging

## Overview
The Verbose LLM Logging feature provides detailed, configurable logging of all LLM (Language Model) interactions in Quizly. This enables debugging, monitoring, and improving AI-powered question generation.

## Features

### Three Verbosity Levels
- **Basic**: Logs metadata and content lengths only (minimal disk usage)
- **Detailed**: Logs truncated prompts/responses (first 1000 chars) - recommended
- **Full**: Logs complete prompts and responses (high disk usage)

### Provider Filtering
- Enable logging for specific providers: Ollama, OpenAI, or both
- Filter log viewing by provider in the UI

### Security
- Automatic API key sanitization using regex patterns
- Prevents accidental exposure of sensitive credentials
- Can be toggled on/off (recommended: keep enabled)

### Metadata Tracking
- Request ID for correlation across logs
- Timing information (duration in milliseconds)
- Status codes and error types
- Token usage (OpenAI only)
- Subject, question count, and generation parameters

## Configuration

### Via Admin Panel UI
1. Navigate to Admin Panel → Logging → Log Levels tab
2. Scroll to "Verbose LLM Logging" section
3. Check "Enable Verbose LLM Logging"
4. Select verbosity level (basic/detailed/full)
5. Select providers to log (Ollama/OpenAI)
6. Configure sanitization (recommended: keep enabled)
7. Click "Save Configuration"

### Via Configuration File
Edit `logging_config.json`:

```json
{
  "llm_verbose_logging": {
    "enabled": true,
    "level": "detailed",
    "providers": ["ollama", "openai"],
    "include_responses": true,
    "include_metadata": true,
    "log_file": "backend/llm_prompts_verbose.log",
    "max_file_size_mb": 50,
    "retention_days": 30,
    "sanitize_api_keys": true
  }
}
```

### Via API
```bash
curl -X PUT http://localhost:8000/api/logging/config \
  -H "Content-Type: application/json" \
  -d '{
    "llm_verbose_logging": {
      "enabled": true,
      "level": "detailed",
      "providers": ["ollama", "openai"]
    }
  }'
```

## Viewing Logs

### Admin Panel UI
1. Navigate to Admin Panel → Logging → Verbose LLM tab
2. View detailed log entries with:
   - Timestamp and provider information
   - Request metadata and timing
   - Full or truncated prompts/responses
   - Error details (if any)
3. Filter by provider using dropdown
4. Refresh to see latest logs
5. Download all logs as file

### Log File Location
Verbose logs are stored in: `logs/backend/llm_prompts_verbose.log`

Each log entry is a JSON object on a single line:
```json
{
  "timestamp": "2025-11-15T19:45:30.123456",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "provider": "openai",
  "model": "gpt-4o-mini",
  "status": "success",
  "status_code": 200,
  "prompt": "Generate 5 multiple-choice questions about...",
  "response": "[{\"text\": \"What is...?\", \"options\": [...]}]",
  "metadata": {
    "subject": "mathematics",
    "limit": 5,
    "questions_generated": 5,
    "total_tokens": 450,
    "prompt_tokens": 120,
    "completion_tokens": 330
  },
  "timing": {
    "start_time": 1700076330.123,
    "end_time": 1700076332.456,
    "duration_ms": 2333
  }
}
```

## Log Management

### Rotation
Logs can be rotated to create backups with timestamps:
```bash
curl -X POST http://localhost:8000/api/logging/verbose-llm-prompts/rotate
```

Or via Admin Panel → Logging → Log Files tab → Rotate button

### Clearing
Clear all verbose logs:
```bash
curl -X POST http://localhost:8000/api/logging/verbose-llm-prompts/clear
```

Or via Admin Panel → Logging → Log Files tab → Clear button

### Downloading
Download complete log file:
```bash
curl -O http://localhost:8000/api/logging/verbose-llm-prompts/download
```

Or via Admin Panel → Logging → Log Files tab → Download button

## Best Practices

### Recommended Settings
- **Level**: `detailed` (balance between detail and disk usage)
- **Providers**: Enable both if using multiple providers
- **Sanitization**: Always keep enabled
- **Max file size**: 50MB (adjust based on usage)
- **Retention**: 30 days (adjust based on compliance requirements)

### Disk Usage Considerations
- **Basic level**: ~1KB per interaction
- **Detailed level**: ~5KB per interaction
- **Full level**: ~20KB per interaction (varies by prompt length)

For 100 questions/day:
- Basic: ~100KB/day, ~3MB/month
- Detailed: ~500KB/day, ~15MB/month
- Full: ~2MB/day, ~60MB/month

### Performance Impact
- **Disabled**: Zero performance impact
- **Enabled**: <1ms overhead per LLM call
- Logging is asynchronous and non-blocking

### Security Considerations
- API keys are automatically redacted
- JWT tokens are sanitized
- Generic API key patterns are detected
- Review logs before sharing externally
- Consider encryption for logs at rest (not implemented)

## Troubleshooting

### Logs not appearing
1. Check if verbose logging is enabled in config
2. Verify provider is selected in config
3. Check file permissions on logs directory
4. Review server logs for errors

### Disk space issues
1. Reduce verbosity level (full → detailed → basic)
2. Decrease max file size
3. Implement log rotation more frequently
4. Clear old logs regularly

### API keys visible in logs
1. Verify sanitization is enabled
2. Check regex patterns in `_sanitize_for_logging()`
3. Report any missed patterns for fixing

## API Reference

### Get Verbose Logs
```
GET /api/logging/verbose-llm-prompts?max_entries=100&provider=ollama
```

### Clear Verbose Logs
```
POST /api/logging/verbose-llm-prompts/clear
```

### Rotate Verbose Logs
```
POST /api/logging/verbose-llm-prompts/rotate
```

### Download Verbose Logs
```
GET /api/logging/verbose-llm-prompts/download
```

### Update Configuration
```
PUT /api/logging/config
Content-Type: application/json

{
  "llm_verbose_logging": {
    "enabled": true,
    "level": "detailed"
  }
}
```

## Future Enhancements
- Log aggregation and search functionality
- Analytics dashboard for LLM usage
- Cost tracking per request
- Performance metrics and trends
- Automatic log archiving
- Elasticsearch integration for log indexing
- Alerting for errors or unusual patterns
