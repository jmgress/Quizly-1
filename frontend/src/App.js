import React, { useState, useEffect } from 'react';
import Quiz from './components/Quiz';
import SubjectSelection from './components/SubjectSelection';
import AdminPanel from './components/AdminPanel';
import './index.css';

function App() {
  const [currentScreen, setCurrentScreen] = useState('home'); // 'home', 'selection', 'quiz', 'admin'
  const [quizConfig, setQuizConfig] = useState(null);
  const [llmConfig, setLlmConfig] = useState(null);
  const [theme, setTheme] = useState(() => {
    // Load theme from localStorage or default to 'light'
    return localStorage.getItem('theme') || 'light';
  });

  useEffect(() => {
    // Check URL hash on load and hash change
    const checkHash = () => {
      const hash = window.location.hash.slice(1); // Remove the '#'
      if (hash === 'admin') {
        setCurrentScreen('admin');
      }
    };

    checkHash(); // Check on initial load
    window.addEventListener('hashchange', checkHash);

    // Fetch LLM configuration for home screen display
    fetchLLMConfig();

    // Apply theme to body
    document.body.setAttribute('data-theme', theme);

    return () => {
      window.removeEventListener('hashchange', checkHash);
    };
    // eslint-disable-next-line
  }, []);

  useEffect(() => {
    // Update theme on change
    document.body.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);
  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  const fetchLLMConfig = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000'}/api/llm/config`);
      if (response.ok) {
        const data = await response.json();
        setLlmConfig(data.config);
      }
    } catch (error) {
      console.error('Failed to fetch LLM config:', error);
    }
  };

  const startQuizSetup = () => {
    setCurrentScreen('selection');
    window.location.hash = ''; // Clear hash
  };

  const handleSubjectSelection = (config) => {
    setQuizConfig(config);
    setCurrentScreen('quiz');
  };

  const restartQuiz = () => {
    setCurrentScreen('home');
    setQuizConfig(null);
    window.location.hash = ''; // Clear hash
  };

  const goToAdmin = () => {
    setCurrentScreen('admin');
    window.location.hash = 'admin';
  };

  const goHome = () => {
    setCurrentScreen('home');
    setQuizConfig(null);
    window.location.hash = ''; // Clear hash
  };

  return (
    <div className="container">
      {/* Theme Toggle UI */}
      <div style={{ position: 'absolute', top: 20, right: 20 }}>
        <button
          className="button"
          aria-label={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
          onClick={toggleTheme}
        >
          {theme === 'light' ? '🌙 Dark Mode' : '☀️ Light Mode'}
        </button>
      </div>

      {currentScreen === 'home' && (
        <div className="home">
          <h1>🧠 Quizly</h1>
          <p>Test your knowledge with our interactive quiz!</p>
          {llmConfig && (
            <div className="llm-info">
              <p className="llm-status">
                🤖 AI Questions powered by <strong>{llmConfig.llm_provider}</strong>
                ({llmConfig.llm_provider === 'ollama' ? llmConfig.ollama_model : llmConfig.openai_model})
              </p>
            </div>
          )}
          <button className="button" onClick={startQuizSetup}>
            Start Quiz
          </button>
          <button className="button" onClick={goToAdmin} style={{ marginTop: '10px', background: '#6c757d' }}>
            Admin Panel
          </button>
        </div>
      )}

      {currentScreen === 'selection' && (
        <SubjectSelection onSelectionComplete={handleSubjectSelection} />
      )}

      {currentScreen === 'quiz' && quizConfig && (
        <Quiz
          onRestart={restartQuiz}
          category={quizConfig.category}
          source={quizConfig.source}
        />
      )}

      {currentScreen === 'admin' && (
        <AdminPanel onGoHome={goHome} />
      )}
    </div>
  );
}

export default App;