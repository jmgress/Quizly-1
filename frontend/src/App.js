import React, { useState, useEffect } from 'react';
import Quiz from './components/Quiz';
import SubjectSelection from './components/SubjectSelection';
import AdminQuestions from './components/AdminQuestions';
import './index.css';

function App() {
  const [currentScreen, setCurrentScreen] = useState('home'); // 'home', 'selection', 'quiz', 'admin'
  const [quizConfig, setQuizConfig] = useState(null);

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
    
    return () => {
      window.removeEventListener('hashchange', checkHash);
    };
  }, []);

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
        <AdminQuestions onGoHome={goHome} />
      )}
    </div>
  );
}

export default App;