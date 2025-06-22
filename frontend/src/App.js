import React, { useState } from 'react';
import Quiz from './components/Quiz';
import SubjectSelection from './components/SubjectSelection';
import './index.css';

function App() {
  const [currentScreen, setCurrentScreen] = useState('home'); // 'home', 'selection', 'quiz'
  const [quizConfig, setQuizConfig] = useState(null);

  const startQuizSetup = () => {
    setCurrentScreen('selection');
  };

  const handleSubjectSelection = (config) => {
    setQuizConfig(config);
    setCurrentScreen('quiz');
  };

  const restartQuiz = () => {
    setCurrentScreen('home');
    setQuizConfig(null);
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
    </div>
  );
}

export default App;