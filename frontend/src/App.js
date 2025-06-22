import React, { useState, useEffect } from 'react';
import Quiz from './components/Quiz';
import './index.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [showQuiz, setShowQuiz] = useState(false);
  const [categories, setCategories] = useState([]);
  const [category, setCategory] = useState('');
  const [aiMode, setAiMode] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/categories`)
      .then((res) => res.json())
      .then((data) => setCategories(data.categories))
      .catch(() => setCategories([]));
  }, []);

  const startQuiz = () => {
    setShowQuiz(true);
  };

  const restartQuiz = () => {
    setShowQuiz(false);
  };

  return (
    <div className="container">
      {!showQuiz ? (
        <div className="home">
          <h1>🧠 Quizly</h1>
          <p>Test your knowledge with our interactive quiz!</p>

          <div style={{ marginBottom: '15px' }}>
            <label>
              Category:
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                style={{ marginLeft: '8px' }}
              >
                <option value="">Any</option>
                {categories.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <label style={{ marginBottom: '15px', display: 'block' }}>
            <input
              type="checkbox"
              checked={aiMode}
              onChange={(e) => setAiMode(e.target.checked)}
            />{' '}
            Use AI-generated questions
          </label>

          <button className="button" onClick={startQuiz}>
            Start Quiz
          </button>
        </div>
      ) : (
        <Quiz onRestart={restartQuiz} category={category} aiMode={aiMode} />
      )}
    </div>
  );
}

export default App;