import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const LoggingSettings = () => {
  const [editConfig, setEditConfig] = useState(null);
  const [logFiles, setLogFiles] = useState([]);
  const [recentLogs, setRecentLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const [activeTab, setActiveTab] = useState('levels');
  const [logFilter, setLogFilter] = useState('all');
  const [llmLoggingEnabled, setLlmLoggingEnabled] = useState(false);
  const [llmLogLevel, setLlmLogLevel] = useState('INFO');

  const LOG_LEVELS = ['ERROR', 'WARN', 'INFO', 'DEBUG', 'TRACE'];
  const LLM_LOG_LEVELS = ['INFO', 'DEBUG', 'TRACE']; // Specific levels for LLM
  const levelToPosition = (level) => LOG_LEVELS.indexOf(level);
  const positionToLevel = (pos) => LOG_LEVELS[pos] || 'INFO';

  useEffect(() => {
    fetchConfig();
    fetchLogFiles();
    fetchRecentLogs();
  }, []);

  const fetchConfig = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/logging/config`);
      const configData = response.data.config;
      setEditConfig({ ...configData });

      // Set LLM logging specific states
      if (configData.llm_prompt_logging) {
        setLlmLoggingEnabled(configData.llm_prompt_logging.enabled);
        setLlmLogLevel(configData.llm_prompt_logging.level);
      } else {
        // Default if not present in config for some reason
        setLlmLoggingEnabled(false);
        setLlmLogLevel('INFO');
      }
      setError(null);
    } catch (err) {
      console.error('Failed to fetch logging config:', err);
      setError('Failed to load logging configuration. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchLogFiles = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/logging/files`);
      setLogFiles(response.data.files);
    } catch (err) {
      console.error('Failed to fetch log files:', err);
    }
  };

  const fetchRecentLogs = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/logging/recent?max_entries=100`);
      setRecentLogs(response.data.logs);
    } catch (err) {
      console.error('Failed to fetch recent logs:', err);
    }
  };

  const handleSaveConfig = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccessMessage('');

      const response = await axios.put(`${API_BASE_URL}/api/logging/config`, editConfig);
      
      setEditConfig(response.data.config);
      setSuccessMessage('Logging configuration saved successfully!');
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage('');
      }, 3000);

    } catch (err) {
      console.error('Failed to save config:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to save logging configuration';
      setError(errorMessage);
    } finally {
      setSaving(false);
    }
  };

  const handleSaveLlmLoggingConfig = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccessMessage('');

      const response = await axios.put(`${API_BASE_URL}/api/logging/llm_prompts_config`, {
        enabled: llmLoggingEnabled,
        level: llmLogLevel,
      });

      // Update state from response if necessary, or assume success
      if (response.data.config && response.data.config.llm_prompt_logging) {
        setLlmLoggingEnabled(response.data.config.llm_prompt_logging.enabled);
        setLlmLogLevel(response.data.config.llm_prompt_logging.level);
      }
      setSuccessMessage('LLM Prompt Logging configuration saved successfully!');

      setTimeout(() => {
        setSuccessMessage('');
      }, 3000);

    } catch (err) {
      console.error('Failed to save LLM prompt logging config:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to save LLM prompt logging configuration';
      setError(errorMessage);
    } finally {
      setSaving(false);
    }
  };

  const handleLogLevelChange = (component, subcomponent, level) => {
    setEditConfig(prev => ({
      ...prev,
      log_levels: {
        ...prev.log_levels,
        [component]: {
          ...prev.log_levels[component],
          [subcomponent]: level
        }
      }
    }));
  };

  const handleClearLogFile = async (filePath) => {
    try {
      await axios.post(`${API_BASE_URL}/api/logging/files/${filePath}/clear`);
      setSuccessMessage(`Log file ${filePath} cleared successfully!`);
      fetchLogFiles();
      fetchRecentLogs();
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('Failed to clear log file:', err);
      setError(`Failed to clear log file: ${err.response?.data?.detail || 'Unknown error'}`);
    }
  };

  const handleRotateLogFile = async (filePath) => {
    try {
      await axios.post(`${API_BASE_URL}/api/logging/files/${filePath}/rotate`);
      setSuccessMessage(`Log file ${filePath} rotated successfully!`);
      fetchLogFiles();
      fetchRecentLogs();
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('Failed to rotate log file:', err);
      setError(`Failed to rotate log file: ${err.response?.data?.detail || 'Unknown error'}`);
    }
  };

  const handleDownloadLogFile = (filePath) => {
    window.open(`${API_BASE_URL}/api/logging/files/${filePath}/download`, '_blank');
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFilteredLogs = () => {
    if (logFilter === 'all') return recentLogs;
    if (logFilter === 'llm_prompts') {
      // Assuming llm prompt logs have a specific component name like 'backend/llm_prompts'
      // Or, if they are JSON, we might check for a specific field if message is an object.
      return recentLogs.filter(log =>
        (log.component && log.component.toLowerCase().includes('llm_prompts')) ||
        (typeof log.message === 'string' && log.message.toLowerCase().includes('llm_event_type')) // Basic check if message is JSON string
      );
    }
    return recentLogs.filter(log => log.level && log.level.toLowerCase().includes(logFilter.toLowerCase()));
  };

  const parseLLMLogMessage = (message) => {
    try {
      const logData = JSON.parse(message);
      // Example: "INFO: OpenAI gpt-3.5-turbo - generate_questions SUCCESS (ID: xyz)"
      // More detailed: "DEBUG: OpenAI gpt-4o-mini - generate_questions - Prompt: Generate... - Response: [{...}] - 1234ms (ID: abc)"
      if (logData.llm_event_type) {
        let preview = `${logData.provider || 'LLM'} ${logData.model || ''} - ${logData.target_function || ''} ${logData.status || ''}`;
        if (logData.request_id) preview += ` (ID: ${logData.request_id.substring(0,6)})`;

        if (logData.log_level === "DEBUG" || logData.log_level === "TRACE") {
            if(logData.prompt) preview += ` - Prompt: ${logData.prompt.substring(0,30)}...`;
        }
        return preview;
      }
    } catch (e) {
      // Not a JSON message or not the expected format, return as is
    }
    return message; // Return original message if not a parsable LLM log
  };

  if (loading) {
    return (
      <div className="logging-settings">
        <div className="loading">Loading logging configuration...</div>
      </div>
    );
  }

  return (
    <div className="logging-settings">
      <div className="settings-header">
        <h3>🔧 Logging Configuration</h3>
        <p>Configure log levels, manage log files, and monitor application activity</p>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {successMessage && (
        <div className="success-message">
          {successMessage}
        </div>
      )}

      <div className="logging-tabs">
        <button 
          className={`tab-button ${activeTab === 'levels' ? 'active' : ''}`}
          onClick={() => setActiveTab('levels')}
        >
          📊 Log Levels
        </button>
        <button 
          className={`tab-button ${activeTab === 'files' ? 'active' : ''}`}
          onClick={() => setActiveTab('files')}
        >
          📁 Log Files
        </button>
        <button 
          className={`tab-button ${activeTab === 'monitor' ? 'active' : ''}`}
          onClick={() => setActiveTab('monitor')}
        >
          👁️ Live Monitor
        </button>
      </div>

      {activeTab === 'levels' && (
        <div className="log-levels-section">
          <h4>Component Log Levels</h4>
          
          <div className="component-group">
            <h5>Frontend Components</h5>
            {editConfig?.log_levels?.frontend && Object.entries(editConfig.log_levels.frontend).map(([component, level]) => (
              <div key={component} className="log-level-control">
                <label>Frontend {component}:</label>
                <div className="log-slider">
                  <input
                    type="range"
                    min="0"
                    max="4"
                    step="1"
                    value={levelToPosition(level)}
                    onChange={(e) =>
                      handleLogLevelChange(
                        'frontend',
                        component,
                        positionToLevel(Number(e.target.value))
                      )
                    }
                    aria-label={`Set log level for frontend ${component}`}
                  />
                  <div className="slider-labels">
                    {LOG_LEVELS.map((lvl, idx) => (
                      <span
                        key={lvl}
                        className={idx === levelToPosition(level) ? 'active' : ''}
                      >
                        {lvl}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="component-group">
            <h5>Backend Components</h5>
            {editConfig?.log_levels?.backend && Object.entries(editConfig.log_levels.backend).map(([component, level]) => (
              <div key={component} className="log-level-control">
                <label>Backend {component}:</label>
                <div className="log-slider">
                  <input
                    type="range"
                    min="0"
                    max="4"
                    step="1"
                    value={levelToPosition(level)}
                    onChange={(e) =>
                      handleLogLevelChange(
                        'backend',
                        component,
                        positionToLevel(Number(e.target.value))
                      )
                    }
                    aria-label={`Set log level for backend ${component}`}
                  />
                  <div className="slider-labels">
                    {LOG_LEVELS.map((lvl, idx) => (
                      <span
                        key={lvl}
                        className={idx === levelToPosition(level) ? 'active' : ''}
                      >
                        {lvl}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="form-actions">
            <button 
              className={`button ${saving ? 'saving' : ''}`}
              onClick={handleSaveConfig}
              disabled={saving}
            >
              {saving ? 'Saving...' : 'Save Configuration'}
            </button>
            
            <button 
              className="button secondary"
              onClick={fetchConfig}
              disabled={saving}
            >
              🔄 Refresh
            </button>
          </div>

          {/* LLM Prompt Logging Section */}
          <div className="llm-prompt-logging-section component-group">
            <h4>LLM Prompt Logging</h4>
            <div className="log-level-control">
              <label htmlFor="llmLoggingEnabledToggle">Enable LLM Prompt Logging:</label>
              <label className="switch">
                <input
                  type="checkbox"
                  id="llmLoggingEnabledToggle"
                  checked={llmLoggingEnabled}
                  onChange={(e) => setLlmLoggingEnabled(e.target.checked)}
                  aria-label="Enable LLM Prompt Logging"
                />
                <span className="slider round"></span>
              </label>
            </div>

            <div className="log-level-control">
              <label htmlFor="llmLogLevelSelect">LLM Logging Level:</label>
              <select
                id="llmLogLevelSelect"
                value={llmLogLevel}
                onChange={(e) => setLlmLogLevel(e.target.value)}
                disabled={!llmLoggingEnabled}
                className="form-select"
                aria-label="Set LLM Logging Level"
              >
                {LLM_LOG_LEVELS.map(level => (
                  <option key={level} value={level}>{level}</option>
                ))}
              </select>
            </div>
            <div className="form-actions">
              <button
                className={`button ${saving ? 'saving' : ''}`}
                onClick={handleSaveLlmLoggingConfig}
                disabled={saving}
              >
                {saving ? 'Saving LLM Config...' : 'Save LLM Log Config'}
              </button>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'files' && (
        <div className="log-files-section">
          <h4>Log File Management</h4>
          
          <div className="file-list">
            {logFiles.map(file => (
              <div key={file.path} className="log-file-item">
                <div className="file-info">
                  <span className="file-name">{file.path}</span>
                  <span className="file-size">{formatFileSize(file.size)}</span>
                  <span className="file-component">{file.component}</span>
                  <span className="file-modified">Modified: {new Date(file.modified).toLocaleString()}</span>
                </div>
                <div className="file-actions">
                  <button 
                    className="button small"
                    onClick={() => handleDownloadLogFile(file.path)}
                  >
                    📥 Download
                  </button>
                  <button 
                    className="button small secondary"
                    onClick={() => handleRotateLogFile(file.path)}
                  >
                    🔄 Rotate
                  </button>
                  <button 
                    className="button small danger"
                    onClick={() => handleClearLogFile(file.path)}
                  >
                    🗑️ Clear
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="form-actions">
            <button 
              className="button secondary"
              onClick={fetchLogFiles}
            >
              🔄 Refresh Files
            </button>
          </div>
        </div>
      )}

      {activeTab === 'monitor' && (
        <div className="log-monitor-section">
          <h4>Live Log Monitor</h4>
          
          <div className="monitor-controls">
            <div className="filter-group">
              <label>Filter by level:</label>
              <select
                value={logFilter}
                onChange={(e) => setLogFilter(e.target.value)}
                className="form-select"
              >
                <option value="all">All Levels</option>
                <option value="error">ERROR</option>
                <option value="warn">WARN</option>
                <option value="info">INFO</option>
                <option value="debug">DEBUG</option>
                <option value="trace">TRACE</option>
                <option value="llm_prompts">LLM Prompts</option>
              </select>
            </div>
            
            <button 
              className="button secondary"
              onClick={fetchRecentLogs}
            >
              🔄 Refresh Logs
            </button>
          </div>

          <div className="log-entries">
            {getFilteredLogs().map((log, index) => (
              <div key={index} className={`log-entry ${log.level.toLowerCase()}`}>
                <span className="log-timestamp">{new Date(log.timestamp).toLocaleString()}</span>
                <span className="log-level">{log.level}</span>
                <span className="log-component">{log.component}</span>
                <span className="log-message">
                  {log.component && log.component.includes('llm_prompts')
                    ? parseLLMLogMessage(log.message)
                    : log.message}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default LoggingSettings;