import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const LoggingSettings = () => {
  const [editConfig, setEditConfig] = useState(null);
  const [logFiles, setLogFiles] = useState([]);
  const [recentLogs, setRecentLogs] = useState([]);
  const [llmPromptLogs, setLlmPromptLogs] = useState([]);
  const [verboseLogs, setVerboseLogs] = useState([]);
  const [verboseLogsInfo, setVerboseLogsInfo] = useState({ enabled: false, level: 'detailed', providers: [] });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const [activeTab, setActiveTab] = useState('levels');
  const [logFilter, setLogFilter] = useState('all');
  const [logTypeFilter, setLogTypeFilter] = useState('all');
  const [verboseProviderFilter, setVerboseProviderFilter] = useState(null);

  const LOG_LEVELS = ['ERROR', 'WARN', 'INFO', 'DEBUG', 'TRACE'];
  const levelToPosition = (level) => LOG_LEVELS.indexOf(level);
  const positionToLevel = (pos) => LOG_LEVELS[pos] || 'INFO';

  useEffect(() => {
    const loadData = async () => {
      await fetchConfig();
      await fetchLogFiles();
      await fetchRecentLogs();
      await fetchLlmPromptLogs();
      await fetchVerboseLogs();
    };
    loadData();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

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

  const fetchVerboseLogs = async () => {
    try {
      const params = verboseProviderFilter ? `?provider=${verboseProviderFilter}` : '';
      const response = await axios.get(`${API_BASE_URL}/api/logging/verbose-llm-prompts${params}`);
      setVerboseLogs(response.data.logs);
      setVerboseLogsInfo({
        enabled: response.data.enabled,
        level: response.data.level,
        providers: response.data.providers
      });
    } catch (err) {
      console.error('Failed to fetch verbose LLM logs:', err);
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

  const handleVerboseLoggingChange = (field, value) => {
    setEditConfig(prev => ({
      ...prev,
      llm_verbose_logging: {
        ...prev.llm_verbose_logging,
        [field]: value
      }
    }));
  };

  const handleVerboseLoggingProviderToggle = (provider) => {
    const currentProviders = editConfig?.llm_verbose_logging?.providers || [];
    const newProviders = currentProviders.includes(provider)
      ? currentProviders.filter(p => p !== provider)
      : [...currentProviders, provider];
    
    handleVerboseLoggingChange('providers', newProviders);
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

  const handleClearVerboseLogs = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/logging/verbose-llm-prompts/clear`);
      setSuccessMessage('Verbose LLM logs cleared successfully!');
      fetchVerboseLogs();
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('Failed to clear verbose LLM logs:', err);
      setError(`Failed to clear verbose LLM logs: ${err.response?.data?.detail || 'Unknown error'}`);
    }
  };

  const handleRotateVerboseLogs = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/logging/verbose-llm-prompts/rotate`);
      setSuccessMessage('Verbose LLM logs rotated successfully!');
      fetchVerboseLogs();
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('Failed to rotate verbose LLM logs:', err);
      setError(`Failed to rotate verbose LLM logs: ${err.response?.data?.detail || 'Unknown error'}`);
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
        <button 
          className={`tab-button ${activeTab === 'verbose' ? 'active' : ''}`}
          onClick={() => setActiveTab('verbose')}
        >
          🔍 Verbose LLM
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

          <div className="component-group">
            <h5>🔍 Verbose LLM Logging</h5>
            <div className="verbose-logging-section">
              <div className="verbose-logging-control">
                <label>
                  <input
                    type="checkbox"
                    checked={editConfig?.llm_verbose_logging?.enabled || false}
                    onChange={(e) => handleVerboseLoggingChange('enabled', e.target.checked)}
                  />
                  Enable Verbose LLM Logging
                </label>
                <p className="setting-description">
                  Log detailed LLM interactions including full prompts, responses, metadata, and token usage
                </p>
              </div>
              
              {editConfig?.llm_verbose_logging?.enabled && (
                <>
                  <div className="verbose-logging-control">
                    <label>Verbosity Level:</label>
                    <select
                      value={editConfig?.llm_verbose_logging?.level || 'detailed'}
                      onChange={(e) => handleVerboseLoggingChange('level', e.target.value)}
                      className="form-select"
                    >
                      <option value="basic">Basic - Metadata and lengths only</option>
                      <option value="detailed">Detailed - Truncated prompts and responses (recommended)</option>
                      <option value="full">Full - Complete prompts and responses</option>
                    </select>
                    <p className="setting-description">
                      {editConfig?.llm_verbose_logging?.level === 'basic' && 'Logs request metadata, timing, and content lengths'}
                      {editConfig?.llm_verbose_logging?.level === 'detailed' && 'Logs first 1000 characters of prompts and responses'}
                      {editConfig?.llm_verbose_logging?.level === 'full' && 'Logs complete content (may use significant disk space)'}
                    </p>
                  </div>

                  <div className="verbose-logging-control">
                    <label>Log Providers:</label>
                    <div className="provider-checkboxes">
                      <label>
                        <input
                          type="checkbox"
                          checked={editConfig?.llm_verbose_logging?.providers?.includes('ollama') || false}
                          onChange={() => handleVerboseLoggingProviderToggle('ollama')}
                        />
                        Ollama
                      </label>
                      <label>
                        <input
                          type="checkbox"
                          checked={editConfig?.llm_verbose_logging?.providers?.includes('openai') || false}
                          onChange={() => handleVerboseLoggingProviderToggle('openai')}
                        />
                        OpenAI
                      </label>
                    </div>
                  </div>

                  <div className="verbose-logging-control">
                    <label>
                      <input
                        type="checkbox"
                        checked={editConfig?.llm_verbose_logging?.sanitize_api_keys !== false}
                        onChange={(e) => handleVerboseLoggingChange('sanitize_api_keys', e.target.checked)}
                      />
                      Sanitize API keys in logs (recommended)
                    </label>
                  </div>

                  <div className="verbose-logging-status">
                    <p>
                      <strong>Log File:</strong> logs/{editConfig?.llm_verbose_logging?.log_file || 'backend/llm_prompts_verbose.log'}
                    </p>
                    <p>
                      <strong>Max Size:</strong> {editConfig?.llm_verbose_logging?.max_file_size_mb || 50} MB
                    </p>
                    <p>
                      <strong>Retention:</strong> {editConfig?.llm_verbose_logging?.retention_days || 30} days
                    </p>
                  </div>
                </>
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

          {editConfig?.llm_verbose_logging?.enabled && (
            <div className="verbose-log-file-section">
              <h5>🔍 Verbose LLM Logs</h5>
              <div className="log-file-item verbose-special">
                <div className="file-info">
                  <span className="file-name">{editConfig?.llm_verbose_logging?.log_file || 'backend/llm_prompts_verbose.log'}</span>
                  <span className="file-component">Verbose LLM Logs</span>
                  <span className="file-status">
                    {verboseLogsInfo.enabled ? '✅ Active' : '⚠️ Disabled'} | 
                    Level: {verboseLogsInfo.level} | 
                    Providers: {verboseLogsInfo.providers.join(', ')}
                  </span>
                </div>
                <div className="file-actions">
                  <button 
                    className="button small"
                    onClick={() => window.open(`${API_BASE_URL}/api/logging/verbose-llm-prompts/download`, '_blank')}
                  >
                    📥 Download
                  </button>
                  <button 
                    className="button small secondary"
                    onClick={handleRotateVerboseLogs}
                  >
                    🔄 Rotate
                  </button>
                  <button 
                    className="button small danger"
                    onClick={handleClearVerboseLogs}
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

      {activeTab === 'verbose' && (
        <div className="verbose-logs-section">
          <h4>🔍 Verbose LLM Logs Viewer</h4>
          
          {!verboseLogsInfo.enabled && (
            <div className="info-message">
              <p>⚠️ Verbose logging is currently disabled. Enable it in the Log Levels tab to start logging detailed LLM interactions.</p>
            </div>
          )}

          {verboseLogsInfo.enabled && (
            <>
              <div className="verbose-logs-status">
                <div className="status-item">
                  <span className="status-label">Status:</span>
                  <span className="status-value active">✅ Active</span>
                </div>
                <div className="status-item">
                  <span className="status-label">Level:</span>
                  <span className="status-value">{verboseLogsInfo.level}</span>
                </div>
                <div className="status-item">
                  <span className="status-label">Providers:</span>
                  <span className="status-value">{verboseLogsInfo.providers.join(', ')}</span>
                </div>
              </div>

              <div className="monitor-controls">
                <div className="filter-group">
                  <label>Filter by provider:</label>
                  <select
                    value={verboseProviderFilter || 'all'}
                    onChange={(e) => {
                      const value = e.target.value === 'all' ? null : e.target.value;
                      setVerboseProviderFilter(value);
                      fetchVerboseLogs();
                    }}
                    className="form-select"
                  >
                    <option value="all">All Providers</option>
                    <option value="ollama">Ollama</option>
                    <option value="openai">OpenAI</option>
                  </select>
                </div>
                
                <button 
                  className="button secondary"
                  onClick={fetchVerboseLogs}
                >
                  🔄 Refresh Logs
                </button>
                
                <button 
                  className="button"
                  onClick={() => window.open(`${API_BASE_URL}/api/logging/verbose-llm-prompts/download`, '_blank')}
                >
                  📥 Download All
                </button>
              </div>

              <div className="verbose-log-entries">
                {verboseLogs.length === 0 && (
                  <p className="no-logs">No verbose logs found. Generate some questions to see LLM interactions logged here.</p>
                )}
                
                {verboseLogs.map((log, index) => (
                  <div key={index} className={`verbose-log-entry ${log.status}`}>
                    <div className="log-header">
                      <span className="log-timestamp">{new Date(log.timestamp).toLocaleString()}</span>
                      <span className="log-provider">{log.provider}</span>
                      <span className="log-model">{log.model}</span>
                      <span className={`log-status ${log.status}`}>{log.status}</span>
                      {log.request_id && <span className="log-request-id" title={log.request_id}>ID: {log.request_id.substring(0, 8)}...</span>}
                    </div>
                    
                    {log.timing && (
                      <div className="log-timing">
                        ⏱️ {log.timing.duration_ms}ms
                      </div>
                    )}

                    {log.metadata && (
                      <div className="log-metadata">
                        <strong>Metadata:</strong>
                        {log.metadata.subject && <span> Subject: {log.metadata.subject}</span>}
                        {log.metadata.limit && <span> | Limit: {log.metadata.limit}</span>}
                        {log.metadata.questions_generated && <span> | Generated: {log.metadata.questions_generated}</span>}
                        {log.metadata.total_tokens && <span> | Tokens: {log.metadata.total_tokens}</span>}
                        {log.status_code && <span> | Status: {log.status_code}</span>}
                      </div>
                    )}

                    {(log.prompt || log.prompt_full) && (
                      <div className="log-prompt">
                        <strong>Prompt:</strong>
                        <pre>{log.prompt_full || log.prompt || `Length: ${log.prompt_length} chars`}</pre>
                      </div>
                    )}

                    {(log.response || log.response_full) && (
                      <div className="log-response">
                        <strong>Response:</strong>
                        <pre>{log.response_full || log.response || `Length: ${log.response_length} chars`}</pre>
                      </div>
                    )}

                    {log.error && (
                      <div className="log-error">
                        <strong>Error:</strong> {log.error}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default LoggingSettings;