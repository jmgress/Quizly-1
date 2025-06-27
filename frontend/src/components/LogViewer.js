import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const LogViewer = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    level: '',
    module: '',
    limit: 50,
    offset: 0
  });
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [logLevel, setLogLevel] = useState(localStorage.getItem('quizly_log_level') || 'INFO');
  const [totalLogs, setTotalLogs] = useState(0);
  const [expandedMessage, setExpandedMessage] = useState(null);

  // Auto-refresh interval
  useEffect(() => {
    let interval;
    if (autoRefresh) {
      interval = setInterval(() => {
        fetchLogs();
      }, 15000); // 15 seconds
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh, filters]);

  // Initial load
  useEffect(() => {
    fetchLogs();
  }, [filters]);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams();
      if (filters.level) params.append('level', filters.level);
      if (filters.module) params.append('module', filters.module);
      params.append('limit', filters.limit.toString());
      params.append('offset', filters.offset.toString());

      const response = await axios.get(`${API_BASE_URL}/api/logs?${params}`);
      setLogs(response.data.logs);
      setTotalLogs(response.data.total);
    } catch (err) {
      setError('Failed to load logs. Please ensure the backend is running.');
      console.error('Error fetching logs:', err);
    } finally {
      setLoading(false);
    }
  };

  const changeLogLevel = async (newLevel) => {
    try {
      await axios.post(`${API_BASE_URL}/api/logs/config`, { level: newLevel });
      setLogLevel(newLevel);
      localStorage.setItem('quizly_log_level', newLevel);
      fetchLogs(); // Refresh logs after level change
    } catch (err) {
      setError(`Failed to change log level: ${err.response?.data?.detail || err.message}`);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value,
      offset: 0 // Reset offset when changing filters
    }));
  };

  const nextPage = () => {
    setFilters(prev => ({
      ...prev,
      offset: prev.offset + prev.limit
    }));
  };

  const prevPage = () => {
    setFilters(prev => ({
      ...prev,
      offset: Math.max(0, prev.offset - prev.limit)
    }));
  };

  const getLogLevelStyle = (level) => {
    switch (level) {
      case 'ERROR':
        return { color: '#dc3545', fontWeight: 'bold' };
      case 'WARNING':
        return { color: '#fd7e14', fontWeight: 'bold' };
      case 'INFO':
        return { color: '#0d6efd', fontWeight: 'bold' };
      case 'DEBUG':
        return { color: '#6c757d' };
      default:
        return {};
    }
  };

  const formatTimestamp = (timestamp) => {
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return timestamp;
    }
  };

  const toggleMessageExpansion = (logId) => {
    setExpandedMessage(expandedMessage === logId ? null : logId);
  };

  const truncateMessage = (message, maxLength = 100) => {
    if (message.length <= maxLength) return message;
    return message.substring(0, maxLength) + '...';
  };

  if (loading && logs.length === 0) {
    return (
      <div className="log-viewer">
        <div className="loading">Loading logs...</div>
      </div>
    );
  }

  return (
    <div className="log-viewer">
      <div className="log-controls">
        <div className="log-filters">
          <div className="filter-group">
            <label>Log Level:</label>
            <select 
              value={filters.level} 
              onChange={(e) => handleFilterChange('level', e.target.value)}
            >
              <option value="">All Levels</option>
              <option value="DEBUG">DEBUG</option>
              <option value="INFO">INFO</option>
              <option value="WARNING">WARNING</option>
              <option value="ERROR">ERROR</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Module:</label>
            <select 
              value={filters.module} 
              onChange={(e) => handleFilterChange('module', e.target.value)}
            >
              <option value="">All Modules</option>
              <option value="api">API</option>
              <option value="database">Database</option>
              <option value="quiz">Quiz</option>
              <option value="admin">Admin</option>
              <option value="ai">AI</option>
              <option value="logs">Logs</option>
              <option value="config">Config</option>
              <option value="startup">Startup</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Show:</label>
            <select 
              value={filters.limit} 
              onChange={(e) => handleFilterChange('limit', parseInt(e.target.value))}
            >
              <option value={25}>25 entries</option>
              <option value={50}>50 entries</option>
              <option value={100}>100 entries</option>
              <option value={200}>200 entries</option>
            </select>
          </div>

          <div className="filter-group">
            <label>
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
              />
              Auto-refresh (15s)
            </label>
          </div>

          <button className="refresh-button" onClick={fetchLogs}>
            Refresh
          </button>
        </div>

        <div className="log-level-config">
          <label>Current Log Level:</label>
          <select 
            value={logLevel} 
            onChange={(e) => changeLogLevel(e.target.value)}
          >
            <option value="DEBUG">DEBUG</option>
            <option value="INFO">INFO</option>
            <option value="WARNING">WARNING</option>
            <option value="ERROR">ERROR</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="error log-error">{error}</div>
      )}

      <div className="log-stats">
        <span>Showing {logs.length} of {totalLogs} logs</span>
        {filters.offset > 0 && (
          <span> (starting from #{filters.offset + 1})</span>
        )}
      </div>

      <div className="log-table-container">
        <table className="log-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Level</th>
              <th>Module</th>
              <th>Message</th>
            </tr>
          </thead>
          <tbody>
            {logs.map(log => (
              <tr key={log.id} className={`log-row log-${log.level.toLowerCase()}`}>
                <td className="timestamp-cell">
                  {formatTimestamp(log.timestamp)}
                </td>
                <td className="level-cell">
                  <span style={getLogLevelStyle(log.level)}>
                    {log.level}
                  </span>
                </td>
                <td className="module-cell">
                  {log.module}
                </td>
                <td className="message-cell">
                  {log.message.length > 100 ? (
                    <div>
                      <span>
                        {expandedMessage === log.id 
                          ? log.message 
                          : truncateMessage(log.message)
                        }
                      </span>
                      <button 
                        className="expand-button"
                        onClick={() => toggleMessageExpansion(log.id)}
                      >
                        {expandedMessage === log.id ? 'Show less' : 'Show more'}
                      </button>
                    </div>
                  ) : (
                    log.message
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {logs.length === 0 && !loading && (
        <div className="no-logs">
          No logs found with current filters.
        </div>
      )}

      <div className="pagination">
        <button 
          onClick={prevPage} 
          disabled={filters.offset === 0}
          className="button"
        >
          Previous
        </button>
        <span className="page-info">
          Page {Math.floor(filters.offset / filters.limit) + 1} of {Math.ceil(totalLogs / filters.limit)}
        </span>
        <button 
          onClick={nextPage} 
          disabled={filters.offset + filters.limit >= totalLogs}
          className="button"
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default LogViewer;