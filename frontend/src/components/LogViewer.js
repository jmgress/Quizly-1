import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const levelColors = {
  ERROR: 'red',
  WARNING: 'orange',
  INFO: 'blue',
  DEBUG: 'gray'
};

const LogViewer = () => {
  const [logs, setLogs] = useState([]);
  const [level, setLevel] = useState(localStorage.getItem('logLevel') || 'INFO');
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchLogs = async () => {
    try {
      const params = { level, limit: 100 };
      const response = await axios.get(`${API_BASE_URL}/api/logs`, { params });
      setLogs(response.data.logs || []);
    } catch (err) {
      console.error('Failed to fetch logs', err);
    }
  };

  const changeLevel = async (newLevel) => {
    setLevel(newLevel);
    localStorage.setItem('logLevel', newLevel);
    try {
      await axios.post(`${API_BASE_URL}/api/loglevel`, { level: newLevel });
      fetchLogs();
    } catch (err) {
      console.error('Failed to set log level', err);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [level]);

  useEffect(() => {
    if (autoRefresh) {
      const id = setInterval(() => fetchLogs(), 15000);
      return () => clearInterval(id);
    }
  }, [autoRefresh, level]);

  return (
    <div>
      <div style={{ marginBottom: '10px' }}>
        <label style={{ marginRight: '10px' }}>Log Level:</label>
        <select value={level} onChange={(e) => changeLevel(e.target.value)}>
          <option value="ERROR">ERROR</option>
          <option value="WARNING">WARNING</option>
          <option value="INFO">INFO</option>
          <option value="DEBUG">DEBUG</option>
        </select>
        <label style={{ marginLeft: '20px' }}>
          <input
            type="checkbox"
            checked={autoRefresh}
            onChange={(e) => setAutoRefresh(e.target.checked)}
          />{' '}
          Auto refresh
        </label>
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
            {logs.map((log, index) => (
              <tr key={index}>
                <td>{log.timestamp}</td>
                <td style={{ color: levelColors[log.level] || 'black' }}>{log.level}</td>
                <td>{log.module}</td>
                <td className="log-message">{log.message}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default LogViewer;
