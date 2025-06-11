import React, { useState } from 'react';
import Quiz from './components/Quiz';
import './index.css';

function App() {
  const [showQuiz, setShowQuiz] = useState(false);

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
          <button className="button" onClick={startQuiz}>
            Start Quiz
          </button>
        </div>
      ) : (
        <Quiz onRestart={restartQuiz} />
      )}
    </div>
  );
}

export default App;