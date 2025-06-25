import React, { useState } from 'react';
import { Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom';
import Quiz from './components/Quiz';
import SubjectSelection from './components/SubjectSelection';
import AdminQuestions from './components/AdminQuestions'; // Import AdminQuestions
import './index.css';

// Home Component
const Home = ({ onStartQuiz }) => (
  <div className="home">
    <h1>🧠 Quizly</h1>
    <p>Test your knowledge with our interactive quiz!</p>
    <button className="button" onClick={onStartQuiz}>
      Start Quiz
    </button>
    <div style={{ marginTop: '20px' }}>
      <Link to="/admin" className="button admin-link">Admin Panel</Link>
    </div>
  </div>
);

function App() {
  const navigate = useNavigate();
  const location = useLocation(); // Used to get state from navigation

  // quizConfig will now be passed via route state or could be managed by a context/global state
  // For simplicity, we'll pass it via state in navigation for now.
  const [quizConfig, setQuizConfig] = useState(location.state?.quizConfig || null);

  const startQuizSetup = () => {
    navigate('/selection');
  };

  const handleSubjectSelection = (config) => {
    setQuizConfig(config); // Set config
    navigate('/quiz', { state: { quizConfig: config } }); // Pass config to Quiz route
  };

  const restartQuiz = () => {
    setQuizConfig(null);
    navigate('/');
  };

  // This effect handles the case where the user navigates directly to /quiz
  // or refreshes the /quiz page. If there's no quizConfig, redirect to home.
  React.useEffect(() => {
    if (location.pathname === '/quiz' && !location.state?.quizConfig && !quizConfig) {
      navigate('/');
    } else if (location.state?.quizConfig && !quizConfig) {
      setQuizConfig(location.state.quizConfig);
    }
  }, [location, navigate, quizConfig]);


  return (
    <div className="container">
      <Routes>
        <Route path="/" element={<Home onStartQuiz={startQuizSetup} />} />
        <Route
          path="/selection"
          element={<SubjectSelection onSelectionComplete={handleSubjectSelection} />}
        />
        <Route
          path="/quiz"
          element={
            quizConfig ? (
              <Quiz
                onRestart={restartQuiz}
                category={quizConfig.category}
                source={quizConfig.source}
              />
            ) : (
              // Redirect or show message if no config (e.g. direct navigation to /quiz)
              // This is a fallback, useEffect above should handle most cases
              <div>Loading quiz or configuration missing... <Link to="/">Go Home</Link></div>
            )
          }
        />
        <Route path="/admin" element={<AdminQuestions />} /> {/* Admin Route */}
      </Routes>
    </div>
  );
}

export default App;