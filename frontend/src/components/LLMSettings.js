import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const LLMSettings = () => {
  const [config, setConfig] = useState(null);
  const [editConfig, setEditConfig] = useState(null);
  const [providersHealth, setProvidersHealth] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const [availableModels, setAvailableModels] = useState({
    ollama: [],
    openai: []
  });

  useEffect(() => {
    fetchConfig();
    fetchProvidersHealth();
    fetchAvailableModels();
  }, []);

  const fetchConfig = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/llm/config`);
      setConfig(response.data.config);
      setEditConfig({ ...response.data.config });
      setError(null);
    } catch (err) {
      console.error('Failed to fetch LLM config:', err);
      setError('Failed to load configuration. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchProvidersHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/llm/providers/health`);
      setProvidersHealth(response.data);
    } catch (err) {
      console.error('Failed to fetch providers health:', err);
    }
  };

  const fetchAvailableModels = async () => {
    try {
      const ollamaResponse = await axios.get(`${API_BASE_URL}/api/models?provider=ollama`);
      const openaiResponse = await axios.get(`${API_BASE_URL}/api/models?provider=openai`);
      
      setAvailableModels({
        ollama: ollamaResponse.data.models || [],
        openai: openaiResponse.data.models || []
      });
    } catch (err) {
      console.error('Failed to fetch available models:', err);
    }
  };

  const handleSaveConfig = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccessMessage('');

      const response = await axios.put(`${API_BASE_URL}/api/llm/config`, editConfig);
      
      setConfig(response.data.config);
      setSuccessMessage('Configuration saved successfully!');
      
      // Refresh health status after config change
      setTimeout(() => {
        fetchProvidersHealth();
      }, 1000);

      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage('');
      }, 3000);

    } catch (err) {
      console.error('Failed to save config:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to save configuration';
      setError(errorMessage);
    } finally {
      setSaving(false);
    }
  };

  const handleConfigChange = (field, value) => {
    setEditConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const getHealthIcon = (provider) => {
    const health = providersHealth[provider];
    if (!health) return '❓';
    return health.healthy ? '✅' : '❌';
  };

  const getHealthText = (provider) => {
    const health = providersHealth[provider];
    if (!health) return 'Unknown';
    if (health.healthy) return 'Healthy';
    return `Error: ${health.error || 'Not available'}`;
  };

  if (loading) {
    return (
      <div className="card">
        <div className="loading">Loading LLM configuration...</div>
      </div>
    );
  }

  if (error && !config) {
    return (
      <div className="card">
        <div className="error">{error}</div>
        <button className="button" onClick={fetchConfig}>
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="llm-settings">
      <div className="settings-section">
        <h3>🤖 LLM Provider Configuration</h3>
        <p>Configure your AI question generation settings</p>

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

        <div className="current-config">
          <h4>Current Configuration</h4>
          <div className="config-display">
            <div className="config-item">
              <span className="config-label">Active Provider:</span>
              <span className="config-value">{config?.llm_provider}</span>
              {getHealthIcon(config?.llm_provider)}
            </div>
            {config?.llm_provider === 'ollama' && (
              <>
                <div className="config-item">
                  <span className="config-label">Ollama Model:</span>
                  <span className="config-value">{config?.ollama_model}</span>
                </div>
                <div className="config-item">
                  <span className="config-label">Ollama Host:</span>
                  <span className="config-value">{config?.ollama_host}</span>
                </div>
              </>
            )}
            {config?.llm_provider === 'openai' && (
              <>
                <div className="config-item">
                  <span className="config-label">OpenAI Model:</span>
                  <span className="config-value">{config?.openai_model}</span>
                </div>
                <div className="config-item">
                  <span className="config-label">API Key:</span>
                  <span className="config-value">{config?.openai_api_key || 'Not configured'}</span>
                </div>
              </>
            )}
          </div>
        </div>

        <div className="provider-health">
          <h4>Provider Health Status</h4>
          <div className="health-grid">
            <div className="health-item">
              <div className="health-header">
                <span className="provider-name">Ollama</span>
                <span className="health-status">{getHealthIcon('ollama')}</span>
              </div>
              <div className="health-details">
                <div className="health-text">{getHealthText('ollama')}</div>
                {providersHealth.ollama && (
                  <>
                    <div className="health-model">Model: {providersHealth.ollama.model}</div>
                    <div className="health-host">Host: {providersHealth.ollama.host}</div>
                  </>
                )}
              </div>
            </div>

            <div className="health-item">
              <div className="health-header">
                <span className="provider-name">OpenAI</span>
                <span className="health-status">{getHealthIcon('openai')}</span>
              </div>
              <div className="health-details">
                <div className="health-text">{getHealthText('openai')}</div>
                {providersHealth.openai && (
                  <>
                    <div className="health-model">Model: {providersHealth.openai.model}</div>
                    <div className="health-api-key">
                      API Key: {providersHealth.openai.api_key_set ? 'Configured' : 'Not configured'}
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="config-form">
          <h4>Update Configuration</h4>
          
          <div className="form-group">
            <label>Provider:</label>
            <select
              value={editConfig?.llm_provider || ''}
              onChange={(e) => handleConfigChange('llm_provider', e.target.value)}
              className="form-select"
            >
              <option value="ollama">Ollama</option>
              <option value="openai">OpenAI</option>
            </select>
          </div>

          {editConfig?.llm_provider === 'ollama' && (
            <>
              <div className="form-group">
                <label>Ollama Model:</label>
                <select
                  value={editConfig?.ollama_model || ''}
                  onChange={(e) => handleConfigChange('ollama_model', e.target.value)}
                  className="form-select"
                >
                  {availableModels.ollama.map(model => (
                    <option key={model} value={model}>{model}</option>
                  ))}
                </select>
              </div>
              
              <div className="form-group">
                <label>Ollama Host:</label>
                <input
                  type="text"
                  value={editConfig?.ollama_host || ''}
                  onChange={(e) => handleConfigChange('ollama_host', e.target.value)}
                  placeholder="http://localhost:11434"
                  className="form-input"
                />
              </div>
            </>
          )}

          {editConfig?.llm_provider === 'openai' && (
            <>
              <div className="form-group">
                <label>OpenAI Model:</label>
                <select
                  value={editConfig?.openai_model || ''}
                  onChange={(e) => handleConfigChange('openai_model', e.target.value)}
                  className="form-select"
                >
                  {availableModels.openai.map(model => (
                    <option key={model} value={model}>{model}</option>
                  ))}
                </select>
              </div>
              
              <div className="form-group">
                <label>OpenAI API Key:</label>
                <input
                  type="password"
                  value={editConfig?.openai_api_key === '***' ? '' : (editConfig?.openai_api_key || '')}
                  onChange={(e) => handleConfigChange('openai_api_key', e.target.value)}
                  placeholder="Enter your OpenAI API key"
                  className="form-input"
                />
                <small className="input-help">
                  Your API key is stored securely and never displayed in full.
                </small>
              </div>
            </>
          )}

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
              onClick={fetchProvidersHealth}
              disabled={saving}
            >
              🔄 Refresh Health
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LLMSettings;