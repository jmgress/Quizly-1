import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const UserResults = () => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API_BASE_URL}/api/quiz/sessions`);
      setSessions(response.data);
    } catch (err) {
      setError('Failed to load quiz sessions. Please try again later.');
      console.error('Error fetching sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="card">
        <div className="loading">Loading results...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="error">{error}</div>
        <button className="button" onClick={fetchSessions}>
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="admin-container">
      <div className="admin-stats">
        <p><strong>Total Sessions:</strong> {sessions.length}</p>
        <p><strong>Average Score:</strong> {sessions.length > 0
          ? (sessions.reduce((acc, curr) => acc + curr.score_percentage, 0) / sessions.length).toFixed(1)
          : 0}%</p>
      </div>

      <table className="results-table" style={{width: '100%', borderCollapse: 'collapse', marginTop: '20px'}}>
        <thead>
          <tr style={{backgroundColor: 'rgba(255, 255, 255, 0.1)', textAlign: 'left'}}>
            <th style={{padding: '12px'}}>Date</th>
            <th style={{padding: '12px'}}>Score</th>
            <th style={{padding: '12px'}}>Correct/Total</th>
            <th style={{padding: '12px'}}>ID</th>
          </tr>
        </thead>
        <tbody>
          {sessions.map(session => (
            <tr key={session.id} style={{borderBottom: '1px solid rgba(255, 255, 255, 0.1)'}}>
              <td style={{padding: '12px'}}>
                {new Date(session.created_at).toLocaleString()}
              </td>
              <td style={{padding: '12px'}}>
                <span className={`score-badge ${session.score_percentage >= 70 ? 'success' : session.score_percentage >= 40 ? 'warning' : 'danger'}`}
                      style={{
                        padding: '4px 8px',
                        borderRadius: '4px',
                        backgroundColor: session.score_percentage >= 70 ? 'rgba(76, 175, 80, 0.2)' : session.score_percentage >= 40 ? 'rgba(255, 152, 0, 0.2)' : 'rgba(244, 67, 54, 0.2)',
                        color: session.score_percentage >= 70 ? '#4caf50' : session.score_percentage >= 40 ? '#ff9800' : '#f44336'
                      }}>
                  {session.score_percentage.toFixed(1)}%
                </span>
              </td>
              <td style={{padding: '12px'}}>
                {session.correct_answers} / {session.total_questions}
              </td>
              <td style={{padding: '12px', fontSize: '0.8em', opacity: 0.7}}>
                {session.id.substring(0, 8)}...
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default UserResults;
