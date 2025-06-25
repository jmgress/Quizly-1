import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const AdminQuestions = () => {
  const [questions, setQuestions] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({});
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchQuestions();
  }, []);

  const fetchQuestions = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/api/questions?limit=1000`);
      setQuestions(res.data);
    } catch (err) {
      setError('Failed to load questions');
    }
  };

  const startEdit = (q) => {
    setEditingId(q.id);
    setFormData({
      text: q.text,
      options: q.options.map(o => ({ ...o })),
      correct_answer: q.correct_answer,
      category: q.category || 'general'
    });
    setMessage(null);
    setError(null);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setFormData({});
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleOptionChange = (index, value) => {
    const opts = [...formData.options];
    opts[index].text = value;
    setFormData(prev => ({ ...prev, options: opts }));
  };

  const saveQuestion = async (id) => {
    if (!formData.text || !formData.options.every(o => o.text) || !formData.correct_answer) {
      setError('Please fill out all fields');
      return;
    }

    try {
      await axios.put(`${API_BASE_URL}/api/questions/${id}`, formData);
      setMessage('Saved!');
      setEditingId(null);
      fetchQuestions();
    } catch (err) {
      setError('Failed to save');
    }
  };

  return (
    <div className="admin-container">
      <h1>Admin - Questions</h1>
      {error && <div className="error">{error}</div>}
      {message && <div className="success">{message}</div>}
      <table className="admin-table">
        <thead>
          <tr>
            <th>Question</th>
            <th>Options</th>
            <th>Answer</th>
            <th>Category</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {questions.map(q => (
            <tr key={q.id}>
              {editingId === q.id ? (
                <>
                  <td>
                    <input
                      value={formData.text}
                      onChange={e => handleChange('text', e.target.value)}
                    />
                  </td>
                  <td>
                    {formData.options.map((opt, i) => (
                      <div key={opt.id}>
                        {opt.id}:
                        <input
                          value={opt.text}
                          onChange={e => handleOptionChange(i, e.target.value)}
                        />
                      </div>
                    ))}
                  </td>
                  <td>
                    <select
                      value={formData.correct_answer}
                      onChange={e => handleChange('correct_answer', e.target.value)}
                    >
                      {formData.options.map(opt => (
                        <option key={opt.id} value={opt.id}>{opt.id}</option>
                      ))}
                    </select>
                  </td>
                  <td>
                    <input
                      value={formData.category}
                      onChange={e => handleChange('category', e.target.value)}
                    />
                  </td>
                  <td>
                    <button onClick={() => saveQuestion(q.id)}>Save</button>
                    <button onClick={cancelEdit}>Cancel</button>
                  </td>
                </>
              ) : (
                <>
                  <td>{q.text}</td>
                  <td>
                    {q.options.map(opt => (
                      <div key={opt.id}>{opt.id}: {opt.text}</div>
                    ))}
                  </td>
                  <td>{q.correct_answer}</td>
                  <td>{q.category}</td>
                  <td>
                    <button onClick={() => startEdit(q)}>Edit</button>
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
