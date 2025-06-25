import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './AdminQuestions.css'; // We'll create this file for styling

const API_BASE_URL = 'http://localhost:8000';

const AdminQuestions = () => {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingQuestionId, setEditingQuestionId] = useState(null);
  const [editFormData, setEditFormData] = useState({});

  const fetchQuestions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/api/questions?limit=1000&admin=true`);
      setQuestions(response.data);
    } catch (err) {
      setError('Failed to load questions. Please try again later.');
      console.error("Fetch questions error:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchQuestions();
  }, [fetchQuestions]);

  const handleEdit = (question) => {
    setEditingQuestionId(question.id);
    setEditFormData({
      text: question.text,
      options: JSON.stringify(question.options, null, 2), // For textarea editing
      correct_answer: question.correct_answer,
      category: question.category,
    });
  };

  const handleCancel = () => {
    setEditingQuestionId(null);
    setEditFormData({});
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setEditFormData({ ...editFormData, [name]: value });
  };

  const validateOptions = (optionsString) => {
    try {
      const options = JSON.parse(optionsString);
      if (!Array.isArray(options)) return false;
      return options.every(opt => typeof opt === 'object' && opt !== null && 'id' in opt && 'text' in opt);
    } catch (e) {
      return false;
    }
  };

  const handleSave = async (questionId) => {
    if (!editFormData.text || !editFormData.category || !editFormData.correct_answer) {
      alert('Question text, category, and correct answer cannot be empty.');
      return;
    }
    if (!validateOptions(editFormData.options)) {
      alert('Options must be a valid JSON array of objects, each with "id" and "text" properties.');
      return;
    }

    const parsedOptions = JSON.parse(editFormData.options);
    const optionIds = parsedOptions.map(opt => opt.id);
    if (!optionIds.includes(editFormData.correct_answer)) {
        alert(`Correct answer "${editFormData.correct_answer}" must be one of the option IDs: ${optionIds.join(', ')}.`);
        return;
    }

    const updatedQuestionData = {
      text: editFormData.text,
      options: parsedOptions,
      correct_answer: editFormData.correct_answer,
      category: editFormData.category,
    };

    try {
      const response = await axios.put(`${API_BASE_URL}/api/questions/${questionId}`, updatedQuestionData);
      setQuestions(questions.map(q => (q.id === questionId ? response.data : q)));
      setEditingQuestionId(null);
      setEditFormData({});
      alert('Question updated successfully!');
    } catch (err) {
      console.error("Update question error:", err.response ? err.response.data : err.message);
      alert(`Failed to update question: ${err.response?.data?.detail || err.message}`);
    }
  };

  if (loading) {
    return <div className="admin-loading">Loading questions...</div>;
  }

  if (error) {
    return <div className="admin-error">{error} <button onClick={fetchQuestions}>Try Again</button></div>;
  }

  return (
    <div className="admin-questions-container">
      <h1>Admin - Manage Quiz Questions</h1>
      <button onClick={fetchQuestions} style={{ marginBottom: '20px' }}>Refresh Questions</button>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Text</th>
            <th>Options</th>
            <th>Correct Answer</th>
            <th>Category</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {questions.map((q) => (
            <tr key={q.id}>
              {editingQuestionId === q.id ? (
                <>
                  <td>{q.id}</td>
                  <td><textarea name="text" value={editFormData.text} onChange={handleInputChange} rows="3" /></td>
                  <td><textarea name="options" value={editFormData.options} onChange={handleInputChange} rows="5" /></td>
                  <td><input type="text" name="correct_answer" value={editFormData.correct_answer} onChange={handleInputChange} /></td>
                  <td><input type="text" name="category" value={editFormData.category} onChange={handleInputChange} /></td>
                  <td>
                    <button onClick={() => handleSave(q.id)}>Save</button>
                    <button onClick={handleCancel}>Cancel</button>
                  </td>
                </>
              ) : (
                <>
                  <td>{q.id}</td>
                  <td>{q.text}</td>
                  <td>
                    <ul>
                      {q.options.map(opt => <li key={opt.id}><strong>{opt.id}:</strong> {opt.text}</li>)}
                    </ul>
                  </td>
                  <td>{q.correct_answer}</td>
                  <td>{q.category}</td>
                  <td>
                    <button onClick={() => handleEdit(q)}>Edit</button>
                  </td>
                </>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AdminQuestions;
