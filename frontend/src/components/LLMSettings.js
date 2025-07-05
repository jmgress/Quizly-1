import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const LLMSettings = () => {
  const [provider, setProvider] = useState('');
  const [model, setModel] = useState('');
  const [providers, setProviders] = useState([]);
  const [models, setModels] = useState([]);
  const [status, setStatus] = useState({});
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const configRes = await axios.get(`${API_BASE_URL}/api/llm/config`);
      setProvider(configRes.data.provider);
      setModel(configRes.data.model);
      await fetchProviders(configRes.data.provider);
    } catch (err) {
      console.error('Failed to load config', err);
    }
  };

  const fetchProviders = async (current) => {
    try {
      const res = await axios.get(`${API_BASE_URL}/api/llm/providers`);
      setProviders(res.data.available.length ? res.data.available : ['ollama']);
      if (current) {
        await fetchModels(current);
        checkHealth(current);
      }
    } catch (err) {
      console.error('Failed to load providers', err);
    }
  };

  const fetchModels = async (prov) => {
    try {
      const res = await axios.get(`${API_BASE_URL}/api/models?provider=${prov}`);
      setModels(res.data.models);
      if (!res.data.models.includes(model)) {
        setModel(res.data.models[0] || '');
      }
    } catch (err) {
      console.error('Failed to load models', err);
    }
  };

  const checkHealth = async (prov) => {
    try {
      const res = await axios.get(`${API_BASE_URL}/api/llm/health?provider=${prov}`);
      setStatus(prev => ({ ...prev, [prov]: res.data.healthy }));
    } catch {
      setStatus(prev => ({ ...prev, [prov]: false }));
    }
  };

  const handleProviderChange = async (val) => {
    setProvider(val);
    await fetchModels(val);
    checkHealth(val);
  };

  const saveConfig = async () => {
    try {
      setSaving(true);
      await axios.put(`${API_BASE_URL}/api/llm/config`, { provider, model });
      setMessage('Configuration saved!');
    } catch (err) {
      setMessage('Failed to save configuration');
    } finally {
      setSaving(false);
      setTimeout(() => setMessage(null), 3000);
    }
  };

  return (
    <div className="llm-settings">
      <h2>LLM Settings</h2>
      <div className="form-group">
        <label>Provider:</label>
        <select value={provider} onChange={e => handleProviderChange(e.target.value)} className="category-select">
          {providers.map(p => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>
        {providers.map(p => (
          <span key={p} className="provider-status">
            {p}: {status[p] ? '✅' : '❌'}
          </span>
        ))}
      </div>
      <div className="form-group">
        <label>Model:</label>
        <select value={model} onChange={e => setModel(e.target.value)} className="category-select">
          {models.map(m => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
      </div>
      <button className="button" onClick={saveConfig} disabled={saving}>
        {saving ? 'Saving...' : 'Save'}
      </button>
      {message && <div className="save-status">{message}</div>}
    </div>
  );
};

export default LLMSettings;
