import React, { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';
import './LogViewer.css'; // We'll create this file for styles

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const LogViewer = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Filters
  const [levelFilter, setLevelFilter] = useState('');
  const [moduleFilter, setModuleFilter] = useState('');
  const [startDateFilter, setStartDateFilter] = useState('');
  const [endDateFilter, setEndDateFilter] = useState('');
  const [messageFilter, setMessageFilter] = useState(''); // New: filter by message content

  // Pagination
  const [limit, setLimit] = useState(50); // Number of logs per page
  const [offset, setOffset] = useState(0); // Current page (offset = page * limit)
  const [totalLogs, setTotalLogs] = useState(0); // Total logs matching filter (approximate, from server if possible or client side)

  // Sorting
  const [sortColumn, setSortColumn] = useState('timestamp');
  const [sortOrder, setSortOrder] = useState('desc');

  // Auto-refresh
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(15); // seconds

  const logLevels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"];

  // Load initial filter level from localStorage or default to ''
  const [levelFilter, setLevelFilter] = useState(() => {
    return localStorage.getItem('logViewerLevelFilter') || '';
  });

  // Save levelFilter to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('logViewerLevelFilter', levelFilter);
  }, [levelFilter]);

  const fetchLogs = useCallback(async (currentOffset = offset, currentLimit = limit) => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        limit: currentLimit,
        offset: currentOffset,
        level: levelFilter || undefined,
        module_filter: moduleFilter || undefined,
        start_time: startDateFilter ? new Date(startDateFilter).toISOString() : undefined,
        end_time: endDateFilter ? new Date(endDateFilter).toISOString() : undefined,
        // message_filter: messageFilter || undefined, // Server doesn't support this yet
      };

      // Client-side sorting for now, as server doesn't sort
      // Server-side pagination is used.

      const response = await axios.get(`${API_BASE_URL}/api/logs`, { params });

      // Client-side filtering for message content
      let fetchedLogs = response.data;
      if (messageFilter) {
        fetchedLogs = fetchedLogs.filter(log => log.message.toLowerCase().includes(messageFilter.toLowerCase()));
      }

      // For now, assuming the API doesn't return total count for pagination with filters.
      // If it did, we'd use that. Otherwise, we can only know total for current view or guess.
      // We'll set logs directly. If we had total, we could calculate totalPages.
      setLogs(fetchedLogs);
      // If API provided total count: setTotalLogs(response.headers['x-total-count'] || response.data.length);
      // For now, we don't have a reliable total count from the backend for filtered results.
      // We are fetching `limit` items, so if we get less than `limit`, it might be the end.

    } catch (err) {
      console.error('Error fetching logs:', err);
      setError(err.response?.data?.detail || 'Failed to fetch logs. Ensure the backend is running and accessible.');
      setLogs([]); // Clear logs on error
    } finally {
      setLoading(false);
    }
  }, [levelFilter, moduleFilter, startDateFilter, endDateFilter, messageFilter, offset, limit]); // Removed sortColumn, sortOrder as server doesn't sort

  useEffect(() => {
    fetchLogs(offset, limit);
  }, [fetchLogs, offset, limit]);

  useEffect(() => {
    let intervalId = null;
    if (autoRefresh) {
      intervalId = setInterval(() => {
        fetchLogs(0, limit); // Refresh first page
        setOffset(0); // Reset to first page on auto-refresh
      }, refreshInterval * 1000);
    }
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [autoRefresh, refreshInterval, fetchLogs, limit]);

  const handleFilterChange = () => {
    setOffset(0); // Reset to first page when filters change
    // fetchLogs will be called by the useEffect monitoring offset and limit
  };

  const clearFilters = () => {
    setLevelFilter('');
    setModuleFilter('');
    setStartDateFilter('');
    setEndDateFilter('');
    setMessageFilter('');
    setOffset(0);
    // fetchLogs will be called by useEffect
  };

  const handleSort = (column) => {
    if (sortColumn === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortOrder('asc');
    }
    // Client-side sorting, so we need to re-sort current logs
  };

  const sortedLogs = useMemo(() => {
    return [...logs].sort((a, b) => {
      const valA = a[sortColumn];
      const valB = b[sortColumn];

      let comparison = 0;
      if (valA > valB) {
        comparison = 1;
      } else if (valA < valB) {
        comparison = -1;
      }
      return sortOrder === 'asc' ? comparison : comparison * -1;
    });
  }, [logs, sortColumn, sortOrder]);


  const getLevelColor = (level) => {
    switch (level.toUpperCase()) {
      case 'ERROR': return 'log-level-error';
      case 'CRITICAL': return 'log-level-error'; // Also red
      case 'WARNING': return 'log-level-warning';
      case 'INFO': return 'log-level-info';
      case 'DEBUG': return 'log-level-debug';
      default: return '';
    }
  };

  const ExpandedMessage = ({ message }) => {
    const [expanded, setExpanded] = useState(false);
    const isLong = message.length > 100; // Consider message long if over 100 chars

    if (!isLong) return <>{message}</>;

    return (
      <>
        {expanded ? message : `${message.substring(0, 100)}...`}
        <button onClick={() => setExpanded(!expanded)} className="expand-button">
          {expanded ? 'Show Less' : 'Show More'}
        </button>
      </>
    );
  };

  // Pagination handlers
  const nextPage = () => {
    // We can only go to the next page if we received a full 'limit' of logs,
    // implying there might be more. This is an optimistic pagination.
    if (logs.length === limit) {
      setOffset(prevOffset => prevOffset + limit);
    }
  };

  const prevPage = () => {
    setOffset(prevOffset => Math.max(0, prevOffset - limit));
  };

  const currentPage = Math.floor(offset / limit) + 1;

  return (
    <div className="log-viewer-container">
      <h2>Application Logs</h2>

      <div className="filters-container card">
        <h4>Filters</h4>
        <div className="filter-grid">
          <div className="filter-item">
            <label htmlFor="levelFilter">Level:</label>
            <select id="levelFilter" value={levelFilter} onChange={e => setLevelFilter(e.target.value)}>
              <option value="">All</option>
              {logLevels.map(lvl => <option key={lvl} value={lvl}>{lvl}</option>)}
            </select>
          </div>
          <div className="filter-item">
            <label htmlFor="moduleFilter">Module/Logger:</label>
            <input type="text" id="moduleFilter" value={moduleFilter} onChange={e => setModuleFilter(e.target.value)} placeholder="e.g., main or quizly"/>
          </div>
          <div className="filter-item">
            <label htmlFor="startDateFilter">Start Date:</label>
            <input type="datetime-local" id="startDateFilter" value={startDateFilter} onChange={e => setStartDateFilter(e.target.value)} />
          </div>
          <div className="filter-item">
            <label htmlFor="endDateFilter">End Date:</label>
            <input type="datetime-local" id="endDateFilter" value={endDateFilter} onChange={e => setEndDateFilter(e.target.value)} />
          </div>
           <div className="filter-item">
            <label htmlFor="messageFilter">Message Contains:</label>
            <input type="text" id="messageFilter" value={messageFilter} onChange={e => setMessageFilter(e.target.value)} placeholder="Text in message"/>
          </div>
        </div>
        <div className="filter-actions">
          <button onClick={handleFilterChange} className="button">Apply Filters</button>
          <button onClick={clearFilters} className="button secondary-button">Clear Filters</button>
        </div>
      </div>

      <div className="controls-container card">
        <h4>Controls</h4>
        <div className="control-item">
          <label htmlFor="autoRefresh">Auto-refresh:</label>
          <input type="checkbox" id="autoRefresh" checked={autoRefresh} onChange={e => setAutoRefresh(e.target.checked)} />
          {autoRefresh && (
            <>
              <label htmlFor="refreshInterval" style={{marginLeft: '10px'}}>Interval (s):</label>
              <input
                type="number"
                id="refreshInterval"
                value={refreshInterval}
                onChange={e => setRefreshInterval(Math.max(5, parseInt(e.target.value, 10)))} // Min 5s
                min="5"
                style={{width: '60px'}}
              />
            </>
          )}
        </div>
        <div className="control-item">
            <label htmlFor="limit">Logs per page:</label>
            <select id="limit" value={limit} onChange={e => { setLimit(Number(e.target.value)); setOffset(0); }}>
                <option value="25">25</option>
                <option value="50">50</option>
                <option value="100">100</option>
                <option value="200">200</option>
            </select>
        </div>
      </div>

      {loading && <div className="loading-indicator">Loading logs...</div>}
      {error && <div className="error-message">Error: {error}</div>}

      <div className="logs-table-container card">
        <div className="pagination-controls">
            <button onClick={prevPage} disabled={offset === 0 || loading} className="button">Previous</button>
            <span> Page {currentPage} </span>
            <button onClick={nextPage} disabled={logs.length < limit || loading} className="button">Next</button>
        </div>
        <table className="logs-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('timestamp')} className="sortable">
                Timestamp {sortColumn === 'timestamp' && (sortOrder === 'asc' ? '▲' : '▼')}
              </th>
              <th onClick={() => handleSort('level')} className="sortable">
                Level {sortColumn === 'level' && (sortOrder === 'asc' ? '▲' : '▼')}
              </th>
              <th onClick={() => handleSort('logger_name')} className="sortable">
                Logger {sortColumn === 'logger_name' && (sortOrder === 'asc' ? '▲' : '▼')}
              </th>
              <th onClick={() => handleSort('module')} className="sortable">
                Module:Line {sortColumn === 'module' && (sortOrder === 'asc' ? '▲' : '▼')}
              </th>
              <th>Message</th>
            </tr>
          </thead>
          <tbody>
            {sortedLogs.length > 0 ? sortedLogs.map((log, index) => (
              <tr key={`${log.timestamp}-${log.module}-${log.line}-${index}`}> {/* More robust key */}
                <td>{new Date(log.timestamp).toLocaleString()}</td>
                <td className={getLevelColor(log.level)}>{log.level}</td>
                <td>{log.logger_name}</td>
                <td>{log.module}:{log.line}</td>
                <td><ExpandedMessage message={log.message} /></td>
              </tr>
            )) : (
              <tr>
                <td colSpan="5">No logs found matching your criteria.</td>
              </tr>
            )}
          </tbody>
        </table>
         <div className="pagination-controls">
            <button onClick={prevPage} disabled={offset === 0 || loading} className="button">Previous</button>
            <span> Page {currentPage} </span>
            <button onClick={nextPage} disabled={logs.length < limit || loading} className="button">Next</button>
        </div>
      </div>
    </div>
  );
};

export default LogViewer;
