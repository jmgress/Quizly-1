import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const LoggingSettings = () => {
  const [editConfig, setEditConfig] = useState(null);
  const [logFiles, setLogFiles] = useState([]);
  const [recentLogs, setRecentLogs] = useState([]);
  const [llmPromptLogs, setLlmPromptLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const [activeTab, setActiveTab] = useState('levels');
  const [logFilter, setLogFilter] = useState('all');
  const [logTypeFilter, setLogTypeFilter] = useState('all');

  const LOG_LEVELS = ['ERROR', 'WARN', 'INFO', 'DEBUG', 'TRACE'];
  const levelToPosition = (level) => LOG_LEVELS.indexOf(level);
  const positionToLevel = (pos) => LOG_LEVELS[pos] || 'INFO';

  useEffect(() => {
    fetchConfig();
    fetchLogFiles();
    fetchRecentLogs();
    fetchLlmPromptLogs();
  }, []);

  const fetchConfig = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/logging/config`);
      setEditConfig({ ...response.data.config });
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

  const fetchLlmPromptLogs = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/logging/llm-prompts?max_entries=100`);
      setLlmPromptLogs(response.data.logs);
    } catch (err) {
      console.error('Failed to fetch LLM prompt logs:', err);
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

  const handleLLMPromptLoggingChange = (field, value) => {
    setEditConfig(prev => ({
      ...prev,
      llm_prompt_logging: {
        ...prev.llm_prompt_logging,
        [field]: value
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

  const handleClearLlmPromptLogs = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/logging/llm-prompts/clear`);
      setSuccessMessage('LLM prompt logs cleared successfully!');
      fetchLlmPromptLogs();
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('Failed to clear LLM prompt logs:', err);
      setError(`Failed to clear LLM prompt logs: ${err.response?.data?.detail || 'Unknown error'}`);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFilteredLogs = () => {
    let logs = [];
    
    // Combine logs based on type filter
    if (logTypeFilter === 'all' || logTypeFilter === 'general') {
      // Add general logs with type marker
      logs = logs.concat(recentLogs.map(log => ({ ...log, logType: 'general' })));
    }
    
    if (logTypeFilter === 'all' || logTypeFilter === 'llm') {
      // Add LLM prompt logs with type marker and formatted display
      logs = logs.concat(llmPromptLogs.map(log => ({
        ...log,
        logType: 'llm',
        component: `${log.provider}/${log.model}`,
        message: log.prompt_preview || log.prompt || 'LLM interaction',
        timestamp: log.timestamp
      })));
    }
    
    // Sort by timestamp
    logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    // Filter by level
    if (logFilter !== 'all') {
      logs = logs.filter(log => log.level.toLowerCase().includes(logFilter.toLowerCase()));
    }
    
    return logs;
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

          <div className="component-group">
            <h5>🤖 LLM Prompt Logging</h5>
            <div className="llm-prompt-section">
              <div className="llm-prompt-control">
                <label>
                  <input
                    type="checkbox"
                    checked={editConfig?.llm_prompt_logging?.enabled || false}
                    onChange={(e) => handleLLMPromptLoggingChange('enabled', e.target.checked)}
                  />
                  Enable LLM Prompt Logging
                </label>
              </div>
              
              {editConfig?.llm_prompt_logging?.enabled && (
                <div className="llm-prompt-control">
                  <label>Logging Level:</label>
                  <select
                    value={editConfig?.llm_prompt_logging?.level || 'INFO'}
                    onChange={(e) => handleLLMPromptLoggingChange('level', e.target.value)}
                    className="form-select"
                  >
                    <option value="INFO">INFO - Basic metadata only</option>
                    <option value="DEBUG">DEBUG - Full prompts and responses</option>
                    <option value="TRACE">TRACE - Complete API calls and errors</option>
                  </select>
                </div>
              )}
            </div>
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

          {editConfig?.llm_prompt_logging?.enabled && (
            <div className="llm-log-file-section">
              <h5>🤖 LLM Prompts Log File</h5>
              <div className="log-file-item llm-special">
                <div className="file-info">
                  <span className="file-name">{editConfig?.llm_prompt_logging?.log_file || 'llm_prompts.log'}</span>
                  <span className="file-component">LLM Prompts</span>
                </div>
                <div className="file-actions">
                  <button 
                    className="button small"
                    onClick={() => window.open(`${API_BASE_URL}/api/logging/llm-prompts/download`, '_blank')}
                  >
                    📥 Download
                  </button>
                  <button 
                    className="button small danger"
                    onClick={handleClearLlmPromptLogs}
                  >
                    🗑️ Clear
                  </button>
                </div>
              </div>
            </div>
          )}

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
              </select>
            </div>
            
            <div className="filter-group">
              <label>Filter by type:</label>
              <select
                value={logTypeFilter}
                onChange={(e) => setLogTypeFilter(e.target.value)}
                className="form-select"
              >
                <option value="all">All Logs</option>
                <option value="general">General Logs</option>
                <option value="llm">LLM Prompts</option>
              </select>
            </div>
            
            <button 
              className="button secondary"
              onClick={() => {
                fetchRecentLogs();
                fetchLlmPromptLogs();
              }}
            >
              🔄 Refresh Logs
            </button>
          </div>

          <div className="log-entries">
            {getFilteredLogs().map((log, index) => (
              <div key={index} className={`log-entry ${log.level.toLowerCase()} ${log.logType === 'llm' ? 'llm-log' : ''}`}>
                <span className="log-timestamp">{new Date(log.timestamp).toLocaleString()}</span>
                <span className="log-level">{log.level}</span>
                <span className="log-component">{log.component}</span>
                {log.logType === 'llm' && (
                  <span className="log-type-badge">🤖 LLM</span>
                )}
                <span className="log-message">{log.message}</span>
                {log.logType === 'llm' && log.timing && (
                  <span className="log-timing">{log.timing.duration_ms}ms</span>
                )}
                {log.logType === 'llm' && log.status && (
                  <span className={`log-status ${log.status}`}>{log.status}</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default LoggingSettings;