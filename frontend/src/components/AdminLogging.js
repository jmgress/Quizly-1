import React, { useState, useEffect, useCallback } from 'react';
import './AdminLogging.css'; // We'll create this CSS file later

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const AdminLogging = () => {
  const [config, setConfig] = useState(null);
  const [initialConfig, setInitialConfig] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const [logLevels] = useState(['ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE']);

  // State for individual level controls
  const [globalLevel, setGlobalLevel] = useState('');
  const [frontendLevel, setFrontendLevel] = useState('');
  const [apiServerLevel, setApiServerLevel] = useState('');
  const [llmProvidersLevel, setLlmProvidersLevel] = useState('');
  const [databaseLevel, setDatabaseLevel] = useState('');

  const [logFiles, setLogFiles] = useState([]);
  const [selectedLogFile, setSelectedLogFile] = useState('');
  const [logEntries, setLogEntries] = useState([]);
  const [logViewerLoading, setLogViewerLoading] = useState(false);
  const [logViewerError, setLogViewerError] = useState('');
  const [logFilterLevel, setLogFilterLevel] = useState('');
  const [logLinesCount, setLogLinesCount] = useState(100);


  const fetchConfig = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_URL}/api/logging/config`);
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || `HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setConfig(data);
      setInitialConfig(JSON.parse(JSON.stringify(data))); // Deep copy for reset

      // Initialize local state for levels
      setGlobalLevel(data.global_level || 'INFO');
      setFrontendLevel(data.frontend_level || 'INFO');
      if (data.backend_levels) {
        setApiServerLevel(data.backend_levels.api_server || 'INFO');
        setLlmProvidersLevel(data.backend_levels.llm_providers || 'INFO');
        setDatabaseLevel(data.backend_levels.database || 'WARNING');
      }
      if (data.log_files) {
        // Convert log_files object to an array of {key, path}
        setLogFiles(Object.entries(data.log_files).map(([key, path]) => ({ key, path })));
        if (Object.keys(data.log_files).length > 0) {
            setSelectedLogFile(Object.keys(data.log_files)[0]); // Default to first log file
        }
      }

    } catch (e) {
      setError(`Failed to fetch logging configuration: ${e.message}`);
      console.error("Fetch config error:", e);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  const handleSaveLogLevels = async () => {
    setError('');
    setSuccessMessage('');
    const payload = {
      global_level: globalLevel,
      frontend_level: frontendLevel, // Note: Frontend level might be indicative, actual control is browser-side
      backend_levels: {
        api_server: apiServerLevel,
        llm_providers: llmProvidersLevel,
        database: databaseLevel,
      },
    };

    try {
      const response = await fetch(`${API_URL}/api/logging/config`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || `HTTP error! status: ${response.status}`);
      }
      const result = await response.json();
      setSuccessMessage(result.message || 'Log levels updated successfully!');
      setConfig(result.config); // Update local config state with response
      setInitialConfig(JSON.parse(JSON.stringify(result.config)));
    } catch (e) {
      setError(`Failed to update log levels: ${e.message}`);
      console.error("Update log levels error:", e);
    }
  };

  const fetchLogEntries = useCallback(async (fileKey, level, lines) => {
    if (!fileKey) return;
    setLogViewerLoading(true);
    setLogViewerError('');
    setLogEntries([]);
    try {
      let url = `${API_URL}/api/logging/logs?component=${fileKey}&lines=${lines}`;
      if (level) {
        url += `&level=${level}`;
      }
      const response = await fetch(url);
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || `HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setLogEntries(data.logs || []);
    } catch (e) {
      setLogViewerError(`Failed to fetch log entries for ${fileKey}: ${e.message}`);
      console.error("Fetch log entries error:", e);
    } finally {
      setLogViewerLoading(false);
    }
  }, []);

  useEffect(() => {
    if (selectedLogFile) {
        fetchLogEntries(selectedLogFile, logFilterLevel, logLinesCount);
    }
  }, [selectedLogFile, logFilterLevel, fetchLogEntries, logLinesCount]);


  const handleFileAction = async (action, logKey) => {
    setError('');
    setSuccessMessage('');
    let url = `${API_URL}/api/logging/actions/${action}/${logKey}`;

    try {
        if (action === 'download') {
            // Open in new tab for download
            window.open(url, '_blank');
            setSuccessMessage(`Download initiated for ${logKey}.`);
            return;
        }

        const response = await fetch(url, { method: 'POST' });
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || `HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        setSuccessMessage(result.message || `Action ${action} on ${logKey} successful.`);

        // If clearing or rotating the currently viewed log, refresh it
        if ((action === 'clear' || action === 'rotate') && logKey === selectedLogFile) {
            fetchLogEntries(selectedLogFile, logFilterLevel, logLinesCount);
        }

    } catch (e) {
        setError(`Failed to perform action ${action} on ${logKey}: ${e.message}`);
        console.error("File action error:", e);
    }
  };


  if (isLoading && !config) return <p>Loading logging configuration...</p>;
  if (error && !config) return <p className="error-message">Error: {error}</p>;
  if (!config) return <p>No logging configuration loaded.</p>;

  return (
    <div className="admin-logging-container">
      <h2>📜 Logging Configuration & Management</h2>

      {error && <p className="error-message">Error: {error}</p>}
      {successMessage && <p className="success-message">{successMessage}</p>}

      {/* Log Level Configuration Section */}
      <div className="logging-section">
        <h3>Log Levels</h3>
        <div className="form-grid">
          {/* Global Level */}
          <div className="form-group">
            <label htmlFor="globalLevel">Backend Global Level:</label>
            <select id="globalLevel" value={globalLevel} onChange={(e) => setGlobalLevel(e.target.value)}>
              {logLevels.map(level => <option key={level} value={level}>{level}</option>)}
            </select>
          </div>
          {/* Frontend Level (Informational) */}
          <div className="form-group">
            <label htmlFor="frontendLevel">Frontend Level (Informational):</label>
            <select id="frontendLevel" value={frontendLevel} onChange={(e) => setFrontendLevel(e.target.value)}>
              {logLevels.map(level => <option key={level} value={level}>{level}</option>)}
            </select>
          </div>
          <div className="form-group full-width"> {/* Placeholder for alignment */} </div>

          {/* Backend Component Levels */}
          <h4>Backend Component Levels:</h4>
          <div className="form-group">
            <label htmlFor="apiServerLevel">API Server:</label>
            <select id="apiServerLevel" value={apiServerLevel} onChange={(e) => setApiServerLevel(e.target.value)}>
              {logLevels.map(level => <option key={level} value={level}>{level}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="llmProvidersLevel">LLM Providers:</label>
            <select id="llmProvidersLevel" value={llmProvidersLevel} onChange={(e) => setLlmProvidersLevel(e.target.value)}>
              {logLevels.map(level => <option key={level} value={level}>{level}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="databaseLevel">Database:</label>
            <select id="databaseLevel" value={databaseLevel} onChange={(e) => setDatabaseLevel(e.target.value)}>
              {logLevels.map(level => <option key={level} value={level}>{level}</option>)}
            </select>
          </div>
        </div>
        <button onClick={handleSaveLogLevels} className="button">Save Log Levels</button>
      </div>

      {/* File Management System Section */}
      <div className="logging-section">
        <h3>Log File Management</h3>
        {config.enable_file_logging ? (
            <>
                <p>Max Log File Size: {(config.log_rotation_max_bytes / (1024*1024)).toFixed(2)} MB, Backup Count: {config.log_rotation_backup_count}</p>
                <table>
                    <thead>
                        <tr>
                            <th>Log File Key</th>
                            <th>Path</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {logFiles.map(({key, path}) => (
                            <tr key={key}>
                                <td>{key}</td>
                                <td>{path}</td>
                                <td>
                                    <button className="button-small" onClick={() => handleFileAction('download', key)}>Download</button>
                                    <button className="button-small" onClick={() => handleFileAction('clear', key)}>Clear</button>
                                    <button className="button-small" onClick={() => handleFileAction('rotate', key)}>Rotate</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </>
        ) : <p>File logging is currently disabled in the configuration.</p>}
      </div>

      {/* Real-time Monitoring Section */}
      <div className="logging-section">
        <h3>Live Log Viewer</h3>
        {config.enable_file_logging ? (
            <>
                <div className="log-viewer-controls">
                    <div className="form-group">
                        <label htmlFor="logFileSelect">View Log:</label>
                        <select id="logFileSelect" value={selectedLogFile} onChange={(e) => setSelectedLogFile(e.target.value)}>
                            <option value="">-- Select Log File --</option>
                            {logFiles.map(({key, path}) => <option key={key} value={key}>{key} ({path})</option>)}
                        </select>
                    </div>
                    <div className="form-group">
                        <label htmlFor="logFilterLevel">Filter by Level:</label>
                        <select id="logFilterLevel" value={logFilterLevel} onChange={(e) => setLogFilterLevel(e.target.value)}>
                            <option value="">ALL</option>
                            {logLevels.map(level => <option key={level} value={level}>{level}</option>)}
                        </select>
                    </div>
                     <div className="form-group">
                        <label htmlFor="logLinesCount">Lines:</label>
                        <input
                            type="number"
                            id="logLinesCount"
                            value={logLinesCount}
                            onChange={(e) => setLogLinesCount(Math.max(10, parseInt(e.target.value,10)))}
                            min="10"
                            max="1000"
                        />
                    </div>
                    <button className="button-small" onClick={() => fetchLogEntries(selectedLogFile, logFilterLevel, logLinesCount)} disabled={logViewerLoading || !selectedLogFile}>
                        {logViewerLoading ? 'Refreshing...' : 'Refresh'}
                    </button>
                </div>
                {logViewerError && <p className="error-message">{logViewerError}</p>}
                <div className="log-viewer">
                    {logViewerLoading && <p>Loading logs...</p>}
                    {!logViewerLoading && logEntries.length === 0 && <p>No log entries to display for current selection, or log file is empty.</p>}
                    <pre>
                        {logEntries.join('\n')}
                    </pre>
                </div>
            </>
        ) : <p>File logging is currently disabled. Log viewer is unavailable.</p>}
      </div>

      {/* Configuration Persistence Display (Read-only) */}
      <div className="logging-section">
        <h3>Current Raw Configuration (Read-only)</h3>
        <pre className="config-display">{JSON.stringify(config, null, 2)}</pre>
      </div>

    </div>
  );
};

export default AdminLogging;
