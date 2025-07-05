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

  useEffect(() => {
    fetchCategories();
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


  const handleStartQuiz = () => {
    const selectedTopic = questionSource === 'ai' ? customTopic : selectedCategory;
    
    if (!selectedTopic) {
      const errorMsg = questionSource === 'ai' 
        ? 'Please enter a custom topic to continue.'
        : 'Please select a subject to continue.';
      setError(errorMsg);
      return;
    }

    const config = {
      category: selectedTopic,
      source: questionSource,
    };

    onSelectionComplete(config);
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

        <button 
          className="button"
          onClick={handleStartQuiz}
          disabled={questionSource === 'database' ? !selectedCategory : !customTopic}
        >
          Start Quiz
        </button>
      </div>
    </div>
  );
};

export default SubjectSelection;