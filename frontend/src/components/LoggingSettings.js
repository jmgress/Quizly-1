import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
const LEVELS = ['ERROR', 'WARNING', 'INFO', 'DEBUG'];

const LoggingSettings = () => {
  const [config, setConfig] = useState(null);
  const [logs, setLogs] = useState([]);
  const [saving, setSaving] = useState(false);

  const fetchConfig = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/api/logging/config`);
      setConfig(res.data.backend ? res.data : { backend: { level: res.data.level } });
    } catch (err) {
      console.error('Failed to fetch logging config', err);
    }
  };

  const fetchLogs = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/api/logging/logs?lines=100`);
      setLogs(res.data.logs || []);
    } catch (err) {
      console.error('Failed to fetch logs', err);
    }
  };

  useEffect(() => {
    fetchConfig();
    fetchLogs();
  }, []);

  const handleLevelChange = (e) => {
    setConfig(prev => ({ ...prev, backend: { ...prev.backend, level: e.target.value } }));
  };

  const saveConfig = async () => {
    try {
      setSaving(true);
      await axios.put(`${API_BASE_URL}/api/logging/config`, { backend: { level: config.backend.level } });
      fetchConfig();
    } catch (err) {
      console.error('Failed to save logging config', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="logging-settings">
      <h3>🔍 Logging Configuration</h3>
      {config && (
        <div className="form-group">
          <label>Backend Log Level:</label>
          <select value={config.backend.level} onChange={handleLevelChange} className="form-select">
            {LEVELS.map(l => <option key={l} value={l}>{l}</option>)}
          </select>
          <button className="button" onClick={saveConfig} disabled={saving}>{saving ? 'Saving...' : 'Save'}</button>
        </div>
      )}
      <div className="log-viewer">
        <h4>Recent Logs</h4>
        <pre className="log-output">
{logs.join('')}
        </pre>
        <button className="button" onClick={fetchLogs}>Refresh</button>
      </div>
    </div>
  );
};

export default LoggingSettings;
