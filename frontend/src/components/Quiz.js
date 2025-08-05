import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Question from './Question';
import ScoreDisplay from './ScoreDisplay';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const Quiz = ({ onRestart, category, source, model }) => {
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [quizComplete, setQuizComplete] = useState(false);
  const [results, setResults] = useState(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [selectedAnswer, setSelectedAnswer] = useState(null);

  useEffect(() => {
    fetchQuestions();
  }, [category, source, model]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchQuestions = async () => {
    try {
      setLoading(true);
      let url;
      
      if (source === 'ai') {
        // Fetch AI-generated questions
        url = `${API_BASE_URL}/api/questions/ai?subject=${encodeURIComponent(category)}&limit=10`;
        if (model) {
          url += `&model=${encodeURIComponent(model)}`;
        }
      } else {
        // Fetch database questions with category filter
        url = `${API_BASE_URL}/api/questions?category=${encodeURIComponent(category)}&limit=10`;
      }
      
      const response = await axios.get(url);
      setQuestions(response.data);
      setLoading(false);
    } catch (err) {
      if (source === 'ai') {
        setError('Failed to generate AI questions. Please ensure Ollama is running with the llama3.2 model, or try using curated questions instead.');
      } else {
        setError('Failed to load questions. Please try again later.');
      }
      setLoading(false);
    }
  };

  const handleAnswerSelect = (questionId, answer) => {
    setSelectedAnswer(answer);
  };

  const handleAnswerSubmit = () => {
    if (!selectedAnswer) return;

    const currentQuestion = questions[currentQuestionIndex];
    const newAnswer = {
      question_id: currentQuestion.id,
      selected_answer: selectedAnswer,
      correct_answer: currentQuestion.correct_answer,
    };

    setAnswers([...answers, newAnswer]);
    setShowFeedback(true);

    // Auto-advance to next question after showing feedback
    setTimeout(() => {
      if (currentQuestionIndex < questions.length - 1) {
        setCurrentQuestionIndex(currentQuestionIndex + 1);
        setSelectedAnswer(null);
        setShowFeedback(false);
      } else {
        // Quiz complete - submit answers
        submitQuiz([...answers, newAnswer]);
      }
    }, 2000);
  };

  const submitQuiz = async (finalAnswers) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/quiz/submit`, {
        answers: finalAnswers
      });
      setResults(response.data);
      setQuizComplete(true);
    } catch (err) {
      setError('Failed to submit quiz. Please try again.');
    }
  };

  const getCurrentQuestion = () => {
    return questions[currentQuestionIndex];
  };

  const getProgress = () => {
    return ((currentQuestionIndex + 1) / questions.length) * 100;
  };

  if (loading) {
    const loadingMessage = source === 'ai' 
      ? `Generating AI questions about ${category}...`
      : `Loading ${category} questions...`;
    
    return (
      <div className="card">
        <div className="loading">{loadingMessage}</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="error">{error}</div>
        <button className="button" onClick={fetchQuestions}>
          Try Again
        </button>
        <button className="button" onClick={onRestart}>
          Back to Home
        </button>
      </div>
    );
  }

  if (quizComplete && results) {
    return (
      <ScoreDisplay 
        results={results} 
        questions={questions}
        onRestart={onRestart}
      />
    );
  }

  if (questions.length === 0) {
    return (
      <div className="card">
        <div className="error">No questions available.</div>
        <button className="button" onClick={onRestart}>
          Back to Home
        </button>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="progress-bar">
        <div 
          className="progress-fill" 
          style={{ width: `${getProgress()}%` }}
        />
      </div>
      
      <div className="quiz-header">
        <p>Question {currentQuestionIndex + 1} of {questions.length}</p>
      </div>

      <Question
        question={getCurrentQuestion()}
        onAnswerSelect={handleAnswerSelect}
        onAnswerSubmit={handleAnswerSubmit}
        selectedAnswer={selectedAnswer}
        showFeedback={showFeedback}
        disabled={showFeedback}
      />
      
      {!showFeedback && (
        <button 
          className="button" 
          onClick={handleAnswerSubmit}
          disabled={!selectedAnswer}
        >
          Submit Answer
        </button>
      )}
    </div>
  );
};

export default Quiz;