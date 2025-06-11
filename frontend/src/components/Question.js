import React from 'react';

const Question = ({ 
  question, 
  onAnswerSelect, 
  selectedAnswer, 
  showFeedback, 
  disabled 
}) => {
  const handleOptionClick = (optionId) => {
    if (!disabled) {
      onAnswerSelect(question.id, optionId);
    }
  };

  const getOptionClass = (option) => {
    let className = 'option-button';
    
    if (selectedAnswer === option.id) {
      className += ' selected';
    }
    
    if (showFeedback) {
      if (option.id === question.correct_answer) {
        className += ' correct';
      } else if (selectedAnswer === option.id && option.id !== question.correct_answer) {
        className += ' incorrect';
      }
    }
    
    return className;
  };

  const getFeedbackMessage = () => {
    if (!showFeedback || !selectedAnswer) return null;
    
    const isCorrect = selectedAnswer === question.correct_answer;
    const correctOption = question.options.find(opt => opt.id === question.correct_answer);
    
    return (
      <div className={`feedback ${isCorrect ? 'correct' : 'incorrect'}`}>
        {isCorrect ? (
          '🎉 Correct! Well done!'
        ) : (
          `❌ Incorrect. The correct answer is: ${correctOption?.text}`
        )}
      </div>
    );
  };

  return (
    <div className="question-card">
      <h2 className="question-text">{question.text}</h2>
      
      <ul className="options-list">
        {question.options.map((option) => (
          <li key={option.id} className="option-item">
            <button
              className={getOptionClass(option)}
              onClick={() => handleOptionClick(option.id)}
              disabled={disabled}
            >
              {option.text}
            </button>
          </li>
        ))}
      </ul>
      
      {getFeedbackMessage()}
    </div>
  );
};

export default Question;