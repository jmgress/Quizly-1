import React, { useState, useEffect } from 'react';
import axios from 'axios';
import LLMSettingsTab from './LLMSettingsTab'; // Import the new component

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const AdminPanel = ({ onGoHome, onConfigUpdate }) => { // Renamed component and added onConfigUpdate
  const [activeTab, setActiveTab] = useState('questions'); // 'questions' or 'llmSettings'
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});
  const [saveStatus, setSaveStatus] = useState({});

  useEffect(() => {
    fetchAllQuestions();
  }, []);

  const fetchAllQuestions = async () => {
    try {
      setLoading(true);
      setError(null);
      // Use high limit to get all questions for admin
      const response = await axios.get(`${API_BASE_URL}/api/questions?limit=1000`);
      setQuestions(response.data);
    } catch (err) {
      setError('Failed to load questions. Please try again later.');
      console.error('Error fetching questions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleEditClick = (question) => {
    setEditingId(question.id);
    setEditForm({
      text: question.text,
      options: question.options.map(opt => ({ ...opt })), // Deep copy
      correct_answer: question.correct_answer,
      category: question.category
    });
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditForm({});
    setSaveStatus(prev => ({ ...prev, [editingId]: null }));
  };

  const handleSaveEdit = async (questionId) => {
    if (!editForm.text?.trim()) {
      setSaveStatus(prev => ({ ...prev, [questionId]: { type: 'error', message: 'Question text is required' } }));
      return;
    }

    // Validate options
    const hasEmptyOptions = editForm.options.some(opt => !opt.text?.trim());
    if (hasEmptyOptions) {
      setSaveStatus(prev => ({ ...prev, [questionId]: { type: 'error', message: 'All option texts are required' } }));
      return;
    }

    // Validate correct answer
    const validIds = editForm.options.map(opt => opt.id);
    if (!validIds.includes(editForm.correct_answer)) {
      setSaveStatus(prev => ({ ...prev, [questionId]: { type: 'error', message: 'Correct answer must match one of the option IDs' } }));
      return;
    }

    try {
      setSaveStatus(prev => ({ ...prev, [questionId]: { type: 'saving', message: 'Saving...' } }));

      const response = await axios.put(`${API_BASE_URL}/api/questions/${questionId}`, {
        text: editForm.text,
        options: editForm.options,
        correct_answer: editForm.correct_answer,
        category: editForm.category
      });

      // Update the question in the local state
      setQuestions(prev => prev.map(q =>
        q.id === questionId ? response.data : q
      ));

      setEditingId(null);
      setEditForm({});
      setSaveStatus(prev => ({ ...prev, [questionId]: { type: 'success', message: 'Saved successfully!' } }));

      // Clear success message after 3 seconds
      setTimeout(() => {
        setSaveStatus(prev => ({ ...prev, [questionId]: null }));
      }, 3000);

    } catch (err) {
      console.error('Error updating question:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to save question';
      setSaveStatus(prev => ({ ...prev, [questionId]: { type: 'error', message: errorMessage } }));
    }
  };

  const handleFormChange = (field, value) => {
    setEditForm(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleOptionChange = (optionIndex, value) => {
    setEditForm(prev => ({
      ...prev,
      options: prev.options.map((opt, index) =>
        index === optionIndex ? { ...opt, text: value } : opt
      )
    }));
  };

  // Conditional rendering for loading/error based on active tab
  if (activeTab === 'questions') {
    if (loading && questions.length === 0) { // Only show main loading if questions aren't there yet
        return (
            <div className="card">
                <div className="loading">Loading questions...</div>
            </div>
        );
    }

    if (error && questions.length === 0) { // Show main error if questions fetch failed
    return (
      <div className="card">
        <div className="error">{error}</div>
        <button className="button" onClick={fetchAllQuestions}>
          Try Again
        </button>
        <button className="button" onClick={onGoHome}>
          Back to Home
        </button>
      </div>
    );
  }

  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>🛠️ Admin Panel</h1>
        <button className="button" onClick={onGoHome} style={{position: 'absolute', top: '20px', right: '20px'}}>
          Back to Home
        </button>
      </div>

      <div className="admin-tabs">
        <button
          className={`tab-button ${activeTab === 'questions' ? 'active' : ''}`}
          onClick={() => setActiveTab('questions')}
        >
          Manage Questions
        </button>
        <button
          className={`tab-button ${activeTab === 'llmSettings' ? 'active' : ''}`}
          onClick={() => setActiveTab('llmSettings')}
        >
          LLM Settings
        </button>
      </div>

      {activeTab === 'questions' && (
        <>
          <h2>Question Management</h2>
          <p>View and edit all quiz questions</p>
          <div className="admin-stats">
            <p><strong>Total Questions:</strong> {questions.length}</p>
            <p><strong>Categories:</strong> {[...new Set(questions.map(q => q.category))].join(', ')}</p>
          </div>

          {loading && <div className="loading">Loading questions...</div>}
          {error && <div className="error">{error} <button onClick={fetchAllQuestions}>Try Again</button></div>}
          {!loading && !error && (
            <div className="questions-table">
              {questions.map(question => (
                <div key={question.id} className="question-row">
                  <div className="question-header">
                    <span className="question-id">ID: {question.id}</span>
                    <span className="question-category">Category: {question.category}</span>
                    {editingId !== question.id && (
                      <button
                        className="edit-button"
                        onClick={() => handleEditClick(question)}
                      >
                        Edit
                      </button>
                    )}
                  </div>

                  {editingId === question.id ? (
                    // Edit mode
                    <div className="edit-form">
                      <div className="form-group">
                        <label>Question Text:</label>
                        <textarea
                          value={editForm.text}
                          onChange={(e) => handleFormChange('text', e.target.value)}
                          rows="3"
                          className="form-input"
                        />
                      </div>

                      <div className="form-group">
                        <label>Category:</label>
                        <input
                          type="text"
                          value={editForm.category}
                          onChange={(e) => handleFormChange('category', e.target.value)}
                          className="form-input"
                        />
                      </div>

                      <div className="form-group">
                        <label>Options:</label>
                        {editForm.options?.map((option, index) => (
                          <div key={option.id} className="option-edit">
                            <span className="option-id">{option.id.toUpperCase()})</span>
                            <input
                              type="text"
                              value={option.text}
                              onChange={(e) => handleOptionChange(index, e.target.value)}
                              className="form-input option-input"
                            />
                            <input
                              type="radio"
                              name={`correct-${question.id}`}
                              checked={editForm.correct_answer === option.id}
                              onChange={() => handleFormChange('correct_answer', option.id)}
                            />
                            <label>Correct</label>
                          </div>
                        ))}
                      </div>

                      <div className="form-actions">
                        <button
                          className="button save-button"
                          onClick={() => handleSaveEdit(question.id)}
                        >
                          Save
                        </button>
                        <button
                          className="button cancel-button"
                          onClick={handleCancelEdit}
                        >
                          Cancel
                        </button>
                      </div>

                      {saveStatus[question.id] && (
                        <div className={`save-status ${saveStatus[question.id].type}`}>
                          {saveStatus[question.id].message}
                        </div>
                      )}
                    </div>
                  ) : (
                    // View mode
                    <div className="question-content">
                      <div className="question-text">
                        <strong>Q:</strong> {question.text}
                      </div>
                      <div className="question-options">
                        {question.options.map(option => (
                          <div
                            key={option.id}
                            className={`option ${option.id === question.correct_answer ? 'correct-option' : ''}`}
                          >
                            <span className="option-id">{option.id.toUpperCase()})</span>
                            <span className="option-text">{option.text}</span>
                            {option.id === question.correct_answer && (
                              <span className="correct-indicator">✓ Correct</span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {saveStatus[question.id] && editingId !== question.id && (
                    <div className={`save-status ${saveStatus[question.id].type}`}>
                      {saveStatus[question.id].message}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {activeTab === 'llmSettings' && (
        <LLMSettingsTab onConfigUpdate={onConfigUpdate} />
      )}
    </div>
  );
};

export default AdminPanel; // Renamed export