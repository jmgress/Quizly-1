import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const LLMSettingsTab = ({ onConfigUpdate }) => {
  const [currentProvider, setCurrentProvider] = useState('');
  const [currentModel, setCurrentModel] = useState('');
  const [availableProviders, setAvailableProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState('');
  const [providerModels, setProviderModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saveStatus, setSaveStatus] = useState({ message: '', type: '' });
  const [healthStatus, setHealthStatus] = useState({});

  const fetchInitialConfig = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/llm/providers`);
      setCurrentProvider(response.data.current_provider);
      setCurrentModel(response.data.current_model);
      setSelectedProvider(response.data.current_provider);
      setSelectedModel(response.data.current_model);

      const providersData = response.data.available_providers.map(p => ({
        name: p.name,
        healthy: p.healthy,
        models: p.models || []
      }));
      setAvailableProviders(providersData);

      // Set models for the initially selected provider
      const initialProviderData = providersData.find(p => p.name === response.data.current_provider);
      if (initialProviderData) {
        setProviderModels(initialProviderData.models);
      }

      // Fetch health for all providers
      providersData.forEach(p => fetchHealthCheck(p.name, false));

    } catch (err) {
      console.error('Error fetching LLM configuration:', err);
      setError('Failed to load LLM configuration. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInitialConfig();
  }, [fetchInitialConfig]);

  const fetchModelsForProvider = async (providerName) => {
    if (!providerName) {
      setProviderModels([]);
      setSelectedModel('');
      return;
    }
    try {
      // Check if models are already available from the /api/llm/providers endpoint
      const providerData = availableProviders.find(p => p.name === providerName);
      if (providerData && providerData.models.length > 0) {
        setProviderModels(providerData.models);
        // Set selected model if current model matches or to the first available
        if (providerData.models.includes(currentModel) && providerName === currentProvider) {
            setSelectedModel(currentModel);
        } else if (providerData.models.length > 0) {
            setSelectedModel(providerData.models[0]);
        } else {
            setSelectedModel('');
        }
      } else { // Fallback to /api/models if not found or empty
        const response = await axios.get(`${API_BASE_URL}/api/models?provider=${providerName}`);
        setProviderModels(response.data.models);
        if (response.data.models.length > 0) {
          setSelectedModel(response.data.models[0]);
        } else {
          setSelectedModel('');
        }
      }
    } catch (err) {
      console.error(`Error fetching models for ${providerName}:`, err);
      setProviderModels([]);
      setSelectedModel('');
      setSaveStatus({ message: `Failed to load models for ${providerName}.`, type: 'error' });
    }
  };

  const fetchHealthCheck = async (providerName, isManualTrigger = true) => {
    if(!providerName) return;
    if (isManualTrigger) {
         setHealthStatus(prev => ({ ...prev, [providerName]: { checking: true, status: '', message: 'Checking...' } }));
    }

    try {
      const response = await axios.get(`${API_BASE_URL}/api/llm/health?provider_name=${providerName}`);
      const isHealthy = response.data.healthy;
      const message = isHealthy ? 'Healthy' : (response.data.error || 'Not Healthy');
      setHealthStatus(prev => ({
        ...prev,
        [providerName]: { checking: false, status: isHealthy ? 'healthy' : 'unhealthy', message }
      }));
    } catch (err) {
      console.error(`Error fetching health for ${providerName}:`, err);
      setHealthStatus(prev => ({
        ...prev,
        [providerName]: { checking: false, status: 'error', message: 'Failed to fetch health status.' }
      }));
    }
  };

  useEffect(() => {
    if (selectedProvider) {
      fetchModelsForProvider(selectedProvider);
      if (!healthStatus[selectedProvider]) { // Fetch health if not already fetched
        fetchHealthCheck(selectedProvider, false);
      }
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedProvider]); // currentModel, currentProvider removed to prevent re-triggering model list on save

  const handleProviderChange = (e) => {
    const newProvider = e.target.value;
    setSelectedProvider(newProvider);
    // Model selection will be updated by the useEffect hook watching selectedProvider
  };

  const handleSaveConfiguration = async () => {
    if (!selectedProvider || !selectedModel) {
      setSaveStatus({ message: 'Please select both a provider and a model.', type: 'error' });
      return;
    }
    setSaveStatus({ message: 'Saving...', type: 'info' });
    try {
      await axios.post(`${API_BASE_URL}/api/llm/config`, {
        provider: selectedProvider,
        model: selectedModel,
      });
      setSaveStatus({ message: 'Configuration saved successfully!', type: 'success' });
      setCurrentProvider(selectedProvider); // Update current display
      setCurrentModel(selectedModel);
      if (onConfigUpdate) {
        onConfigUpdate(); // Notify App.js to re-fetch and update display
      }
      // Refetch health for the newly saved provider as it might have changed
      fetchHealthCheck(selectedProvider);
    } catch (err) {
      console.error('Error saving LLM configuration:', err);
      setSaveStatus({ message: err.response?.data?.detail || 'Failed to save configuration.', type: 'error' });
    } finally {
        setTimeout(() => setSaveStatus({ message: '', type: '' }), 5000);
    }
  };

  if (loading) {
    return <div className="loading">Loading LLM Settings...</div>;
  }

  if (error) {
    return <div className="error">{error} <button onClick={fetchInitialConfig}>Try Again</button></div>;
  }

  return (
    <div className="llm-settings-tab card">
      <h2>LLM Provider Configuration</h2>
      <p>Manage settings for AI-powered question generation.</p>

      <div className="current-config-display">
        <strong>Currently Active:</strong> Provider: <span className="provider-value">{currentProvider}</span>, Model: <span className="model-value">{currentModel}</span>
      </div>

      <div className="form-group">
        <label htmlFor="provider-select">LLM Provider:</label>
        <select
          id="provider-select"
          value={selectedProvider}
          onChange={handleProviderChange}
          className="form-input"
        >
          <option value="">Select a Provider</option>
          {availableProviders.map(p => (
            <option key={p.name} value={p.name}>
              {p.name.charAt(0).toUpperCase() + p.name.slice(1)}
              {healthStatus[p.name] && (
                healthStatus[p.name].checking ? ' (checking health...)' :
                healthStatus[p.name].status === 'healthy' ? ' (Healthy)' :
                healthStatus[p.name].status === 'unhealthy' ? ' (Unhealthy)' :
                healthStatus[p.name].status === 'error' ? ' (Health Check Error)' : ' (Health N/A)'
              )}
            </option>
          ))}
        </select>
        {selectedProvider && (
            <button
                onClick={() => fetchHealthCheck(selectedProvider)}
                disabled={healthStatus[selectedProvider]?.checking}
                className="button health-check-btn"
            >
                {healthStatus[selectedProvider]?.checking ? 'Checking...' : 'Refresh Health'}
            </button>
        )}
         {healthStatus[selectedProvider] && !healthStatus[selectedProvider].checking && (
            <span className={`health-status-message ${healthStatus[selectedProvider].status}`}>
                {healthStatus[selectedProvider].message}
            </span>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="model-select">Model:</label>
        <select
          id="model-select"
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
          disabled={!selectedProvider || providerModels.length === 0}
          className="form-input"
        >
          <option value="">{selectedProvider ? (providerModels.length === 0 ? 'No models found or provider unavailable' : 'Select a Model') : 'Select provider first'}</option>
          {providerModels.map(m => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
        {selectedProvider && providerModels.length === 0 && !loading && (
            <small className="input-help">
                Could not load models. The provider might be unavailable or has no models configured.
            </small>
        )}
      </div>

      <button
        className="button save-button"
        onClick={handleSaveConfiguration}
        disabled={!selectedProvider || !selectedModel || saveStatus.type === 'info'}
      >
        {saveStatus.type === 'info' ? 'Saving...' : 'Save Configuration'}
      </button>

      {saveStatus.message && (
        <div className={`save-status ${saveStatus.type}`} style={{marginTop: '10px'}}>
          {saveStatus.message}
        </div>
      )}
    </div>
  );
};

export default LLMSettingsTab;
