import React, { useState, useEffect } from 'react';
import Quiz from './components/Quiz';
import SubjectSelection from './components/SubjectSelection';
import AdminPanel from './components/AdminPanel'; // Updated import
import './index.css';

function App() {
  const [currentScreen, setCurrentScreen] = useState('home'); // 'home', 'selection', 'quiz', 'admin'
  const [quizConfig, setQuizConfig] = useState(null);
  const [llmConfig, setLlmConfig] = useState({ provider: 'N/A', model: 'N/A' });

  useEffect(() => {
    fetchLlmConfig();
    // Check URL hash on load and hash change
    const checkHash = () => {
      const hash = window.location.hash.slice(1); // Remove the '#'
      if (hash === 'admin') {
        setCurrentScreen('admin');
      }
    };

    checkHash(); // Check on initial load
    window.addEventListener('hashchange', checkHash);
    
    return () => {
      window.removeEventListener('hashchange', checkHash);
    };
  }, []);

  const fetchLlmConfig = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000'}/api/llm/config`);
      if (!response.ok) {
        throw new Error('Failed to fetch LLM config');
      }
      const data = await response.json();
      setLlmConfig(data);
    } catch (error) {
      console.error("Error fetching LLM config:", error);
      setLlmConfig({ provider: 'Error', model: 'Error fetching config' });
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
      {currentScreen === 'home' && (
        <div className="home">
          <h1>🧠 Quizly</h1>
          <p>Test your knowledge with our interactive quiz!</p>
          <button className="button" onClick={startQuizSetup}>
            Start Quiz
          </button>
          <button className="button" onClick={goToAdmin} style={{ marginTop: '10px', background: '#6c757d' }}>
            Admin Panel
          </button>
          <p style={{ marginTop: '20px', fontSize: '0.9em', color: '#666' }}>
            AI Questions powered by {llmConfig.provider} ({llmConfig.model})
          </p>
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
          // model prop is no longer needed here as backend uses global config
        />
      )}

      {currentScreen === 'admin' && (
        <AdminPanel onGoHome={goHome} onConfigUpdate={fetchLlmConfig} />
      )}
    </div>
  );
}

export default App;