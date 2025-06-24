import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const SubjectSelection = ({ onSelectionComplete }) => {
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [customCategory, setCustomCategory] = useState('');
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
    const categoryToUse = questionSource === 'ai' ? customCategory : selectedCategory;

    if (!categoryToUse) {
      setError('Please select or enter a subject to continue.');
      return;
    }
    setError(null); // Clear any previous error

    onSelectionComplete({
      category: categoryToUse,
      source: questionSource
    });
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
        {questionSource === 'database' && (
          <div className="form-group">
            <label htmlFor="category-select">Subject (Curated):</label>
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
        )}

        {questionSource === 'ai' && (
          <div className="form-group">
            <label htmlFor="custom-category-input">Subject (AI):</label>
            <input
              type="text"
              id="custom-category-input"
              value={customCategory}
              onChange={(e) => setCustomCategory(e.target.value)}
              placeholder="Enter any topic (e.g., 'Roman History')"
              className="category-input"
            />
            <small>Enter a topic for AI-generated questions.</small>
          </div>
        )}

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
                <small>High-quality pre-written questions</small>
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
                <small>Fresh questions powered by Ollama</small>
              </span>
            </label>
          </div>
        </div>

        <button
          className="button"
          onClick={handleStartQuiz}
          disabled={
            (questionSource === 'database' && !selectedCategory) ||
            (questionSource === 'ai' && !customCategory)
          }
        >
          Start Quiz
        </button>
      </div>
    </div>
  );
};

export default SubjectSelection;