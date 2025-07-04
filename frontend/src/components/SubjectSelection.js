import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const SubjectSelection = ({ onSelectionComplete }) => {
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [customTopic, setCustomTopic] = useState('');
  const [questionSource, setQuestionSource] = useState('database'); // 'database' or 'ai'
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // State for AI model selection
  const [availableModels, setAvailableModels] = useState({}); // Stores all models fetched from API, keyed by provider
  const [selectedModel, setSelectedModel] = useState(''); // ID of the currently selected AI model
  const [currentProvider, setCurrentProvider] = useState(null); // ID of the default AI provider (e.g., 'ollama', 'openai')
  const [loadingModels, setLoadingModels] = useState(false); // True while fetching models (currently not used, but good for future)

  useEffect(() => {
    // Fetch initial data: categories, AI providers, and all AI models
    const fetchInitialData = async () => {
      setLoading(true);
      try {
        // Fetch standard quiz categories
        const categoriesResponse = await axios.get(`${API_BASE_URL}/api/categories`);
        setCategories(categoriesResponse.data.categories);

        // Fetch available LLM providers and determine the current default provider
        const providersResponse = await axios.get(`${API_BASE_URL}/api/llm/providers`);
        const defaultProvider = providersResponse.data.current; // e.g., 'ollama' or 'openai'
        setCurrentProvider(defaultProvider);

        // Fetch all available AI models from the API
        const modelsResponse = await axios.get(`${API_BASE_URL}/api/models`);
        setAvailableModels(modelsResponse.data); // e.g., { openai: [...], ollama: [...] }

        // Attempt to load the last selected model for the current default provider from local storage
        if (defaultProvider && modelsResponse.data[defaultProvider] && modelsResponse.data[defaultProvider].length > 0) {
          const lastSelectedModel = localStorage.getItem(`lastSelectedModel_${defaultProvider}`);
          // Check if the last selected model is valid for the current provider
          if (lastSelectedModel && modelsResponse.data[defaultProvider].find(m => m.id === lastSelectedModel)) {
            setSelectedModel(lastSelectedModel);
          } else {
            // If no valid last selection, default to the first model of the current provider
            setSelectedModel(modelsResponse.data[defaultProvider][0].id);
          }
        }

      } catch (err) {
        setError('Failed to load initial data. Please try again later.');
        console.error("Error fetching initial data:", err);
      }
      setLoading(false);
    };

    fetchInitialData();
  }, []); // Runs once on component mount

  useEffect(() => {
    // This effect ensures that if the currentProvider changes, or if models finish loading,
    // the selectedModel state is correctly initialized or updated.
    // It prioritizes local storage, then the first available model for the provider.
    if (currentProvider && availableModels[currentProvider] && availableModels[currentProvider].length > 0) {
      const lastSelectedModel = localStorage.getItem(`lastSelectedModel_${currentProvider}`);
      if (lastSelectedModel && availableModels[currentProvider].find(m => m.id === lastSelectedModel)) {
        // If a valid model was previously selected for this provider, use it
        if (selectedModel !== lastSelectedModel) setSelectedModel(lastSelectedModel);
      } else if (!selectedModel || !availableModels[currentProvider].find(m => m.id === selectedModel)) {
        // If no model is selected, or the current selection is invalid for this provider,
        // default to the first available model for this provider.
        setSelectedModel(availableModels[currentProvider][0].id);
      }
    }
  }, [currentProvider, availableModels, selectedModel]); // Re-run if these dependencies change


  // Handles changes to the AI model selection dropdown
  const handleModelChange = (e) => {
    const newModelId = e.target.value;
    setSelectedModel(newModelId);
    // Store the newly selected model in local storage for the current provider
    if (currentProvider) {
      localStorage.setItem(`lastSelectedModel_${currentProvider}`, newModelId);
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

    const quizConfig = {
      category: selectedTopic,
      source: questionSource,
    };

    if (questionSource === 'ai' && selectedModel) {
      quizConfig.model = selectedModel;
      if (currentProvider) { // Save last selected model for this provider
        localStorage.setItem(`lastSelectedModel_${currentProvider}`, selectedModel);
      }
    }

    onSelectionComplete(quizConfig);
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
        )}

        {questionSource === 'ai' && currentProvider && availableModels[currentProvider] && (
          <div className="form-group">
            <label htmlFor="model-select">AI Model ({currentProvider}):</label>
            <select
              id="model-select"
              value={selectedModel}
              onChange={handleModelChange}
              className="category-select" // Re-use existing style for now
              disabled={loadingModels}
            >
              {loadingModels ? (
                <option value="">Loading models...</option>
              ) : (
                availableModels[currentProvider].map((model) => (
                  <option key={model.id} value={model.id} title={model.description}>
                    {model.name}
                  </option>
                ))
              )}
            </select>
            {availableModels[currentProvider]?.find(m => m.id === selectedModel)?.description && (
              <small className="input-help">
                {availableModels[currentProvider].find(m => m.id === selectedModel).description}
              </small>
            )}
          </div>
        )}

        <button 
          className="button"
          onClick={handleStartQuiz}
          disabled={
            (questionSource === 'database' ? !selectedCategory : !customTopic) ||
            (questionSource === 'ai' && !selectedModel)
          }
        >
          Start Quiz
        </button>
      </div>
    </div>
  );
};

export default SubjectSelection;