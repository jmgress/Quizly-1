import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const SubjectSelection = ({ onSelectionComplete }) => {
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [customTopic, setCustomTopic] = useState('');
  const [questionSource, setQuestionSource] = useState('database'); // 'database' or 'ai'
  const [availableModels, setAvailableModels] = useState({});
  const [selectedProvider, setSelectedProvider] = useState('ollama');
  const [selectedModel, setSelectedModel] = useState('');
  const [defaultModels, setDefaultModels] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCategories();
    fetchAvailableModels();
  }, []);

  const fetchCategories = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/categories`);
      setCategories(response.data.categories);
      setLoading(false);
    } catch (err) {
      setError('Failed to load categories. Please try again later.');
      setLoading(false);
    }
  };

  const fetchAvailableModels = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/models`);
      const modelsData = response.data.models || {};
      const defaultData = response.data.default || {};
      
      setAvailableModels(modelsData);
      setDefaultModels(defaultData);
      
      // Set initial provider and model based on what's available
      const providers = Object.keys(modelsData);
      if (providers.length > 0) {
        const defaultProvider = providers.includes('ollama') ? 'ollama' : providers[0];
        setSelectedProvider(defaultProvider);
        setSelectedModel(defaultData[defaultProvider] || '');
      } else {
        // No models available, use defaults
        setSelectedProvider('ollama');
        setSelectedModel('llama3.2');
      }
    } catch (err) {
      console.error('Failed to fetch available models:', err);
      // Don't set error state, just use defaults
      setSelectedProvider('ollama');
      setSelectedModel('llama3.2');
    }
  };

  const handleStartQuiz = () => {
    const selectedTopic = questionSource === 'ai' ? customTopic : selectedCategory;
    
    if (!selectedTopic) {
      const errorMsg = questionSource === 'ai' 
        ? 'Please enter a custom topic to continue.'
        : 'Please select a subject to continue.';
      setError(errorMsg);
      return;
    }

    // For AI questions, ensure provider and model are selected
    if (questionSource === 'ai' && (!selectedProvider || !selectedModel)) {
      setError('Please select an AI provider and model.');
      return;
    }

    onSelectionComplete({
      category: selectedTopic,
      source: questionSource,
      provider: questionSource === 'ai' ? selectedProvider : null,
      model: questionSource === 'ai' ? selectedModel : null
    });
  };

  const handleProviderChange = (provider) => {
    setSelectedProvider(provider);
    // Set default model for the selected provider
    if (defaultModels[provider]) {
      setSelectedModel(defaultModels[provider]);
    } else if (availableModels[provider] && availableModels[provider].length > 0) {
      setSelectedModel(availableModels[provider][0].id);
    } else {
      setSelectedModel('');
    }
  };

  const getModelDescription = (model) => {
    if (!model) return '';
    
    for (const provider in availableModels) {
      const providerModels = availableModels[provider];
      const modelInfo = providerModels.find(m => m.id === model);
      if (modelInfo) {
        return `${modelInfo.description} (Speed: ${modelInfo.speed}, Cost: ${modelInfo.cost}, Quality: ${modelInfo.quality})`;
      }
    }
    return '';
  };

  if (loading) {
    return (
      <div className="card">
        <div className="loading">Loading subjects...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="error">{error}</div>
        <button className="button" onClick={fetchCategories}>
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="card">
      <h2>🎯 Select Your Quiz Subject</h2>
      <p>Choose a subject and question source to start your personalized quiz!</p>

      <div className="subject-selection">
        <div className="form-group">
          <label>Question Source:</label>
          <div className="radio-group">
            <label className="radio-label">
              <input
                type="radio"
                name="questionSource"
                value="database"
                checked={questionSource === 'database'}
                onChange={(e) => setQuestionSource(e.target.value)}
              />
              <span className="radio-text">
                📚 Curated Questions
                <small>High-quality pre-written questions from predefined categories</small>
              </span>
            </label>
            <label className="radio-label">
              <input
                type="radio"
                name="questionSource"
                value="ai"
                checked={questionSource === 'ai'}
                onChange={(e) => setQuestionSource(e.target.value)}
              />
              <span className="radio-text">
                🤖 AI-Generated Questions
                <small>Fresh questions powered by Ollama - enter any custom topic!</small>
              </span>
            </label>
          </div>
        </div>

        {questionSource === 'database' ? (
          <div className="form-group">
            <label htmlFor="category-select">Subject:</label>
            <select
              id="category-select"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="category-select"
            >
              <option value="">Choose a subject...</option>
              {categories.map((category) => (
                <option key={category} value={category}>
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </option>
              ))}
            </select>
          </div>
        ) : (
          <>
            <div className="form-group">
              <label htmlFor="custom-topic">Custom Topic:</label>
              <input
                id="custom-topic"
                type="text"
                value={customTopic}
                onChange={(e) => setCustomTopic(e.target.value)}
                placeholder="Enter any topic you want to be quizzed on..."
                className="custom-topic-input"
              />
              <small className="input-help">
                Examples: "Ancient Rome", "JavaScript Programming", "Marine Biology", "Medieval History"
              </small>
            </div>
            
            {Object.keys(availableModels).length > 0 && (
              <>
                <div className="form-group">
                  <label>AI Provider:</label>
                  <div className="radio-group">
                    {Object.keys(availableModels).map(provider => (
                      <label key={provider} className="radio-label">
                        <input
                          type="radio"
                          name="provider"
                          value={provider}
                          checked={selectedProvider === provider}
                          onChange={(e) => handleProviderChange(e.target.value)}
                        />
                        <span className="radio-text">
                          {provider === 'openai' ? '🤖 OpenAI' : '🏠 Ollama (Local)'}
                          <small>
                            {provider === 'openai' 
                              ? 'Cloud-based AI with premium models' 
                              : 'Local AI models, free to use'}
                          </small>
                        </span>
                      </label>
                    ))}
                  </div>
                </div>

                {availableModels[selectedProvider] && (
                  <div className="form-group">
                    <label htmlFor="model-select">AI Model:</label>
                    <select
                      id="model-select"
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      className="category-select"
                    >
                      <option value="">Choose a model...</option>
                      {availableModels[selectedProvider].map((model) => (
                        <option key={model.id} value={model.id}>
                          {model.name}
                        </option>
                      ))}
                    </select>
                    {selectedModel && (
                      <small className="input-help">
                        {getModelDescription(selectedModel)}
                      </small>
                    )}
                  </div>
                )}
              </>
            )}
          </>
        )}

        <button 
          className="button"
          onClick={handleStartQuiz}
          disabled={
            questionSource === 'database' 
              ? !selectedCategory 
              : !customTopic || (Object.keys(availableModels).length > 0 && (!selectedProvider || !selectedModel))
          }
        >
          Start Quiz
        </button>
      </div>
    </div>
  );
};

export default SubjectSelection;