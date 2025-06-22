import React from 'react';

const ScoreDisplay = ({ results, questions, onRestart }) => {
  const getScoreMessage = () => {
    const percentage = results.score_percentage;
    
    if (percentage >= 90) {
      return "🏆 Excellent! You're a quiz master!";
    } else if (percentage >= 70) {
      return "🎉 Great job! Well done!";
    } else if (percentage >= 50) {
      return "👍 Good effort! Keep practicing!";
    } else {
      return "📚 Keep studying and try again!";
    }
  };

  const getQuestionById = (questionId) => {
    return questions.find(q => q.id === questionId);
  };

  const getOptionText = (question, optionId) => {
    const option = question?.options.find(opt => opt.id === optionId);
    return option?.text || 'Unknown';
  };

  // Get original question number based on the order questions were presented
  const getOriginalQuestionNumber = (questionId) => {
    const questionIndex = questions.findIndex(q => q.id === questionId);
    return questionIndex >= 0 ? questionIndex + 1 : '?';
  };

  // Sort answers to match original question order for consistent display
  const getSortedAnswers = () => {
    return [...results.answers].sort((a, b) => {
      const indexA = questions.findIndex(q => q.id === a.question_id);
      const indexB = questions.findIndex(q => q.id === b.question_id);
      return indexA - indexB;
    });
  };

  return (
    <div className="card">
      <div className="score-display">
        <h2>🎯 Quiz Complete!</h2>
        
        <div className="score-number">
          {results.correct_answers}/{results.total_questions}
        </div>
        
        <div className="score-message">
          {Math.round(results.score_percentage)}% Correct
        </div>
        
        <p>{getScoreMessage()}</p>
        
        <div style={{ marginTop: '30px', textAlign: 'left' }}>
          <h3>📋 Review Your Answers:</h3>
          
          {getSortedAnswers().map((answer) => {
            const question = getQuestionById(answer.question_id);
            if (!question) return null;
            
            const questionNumber = getOriginalQuestionNumber(answer.question_id);
            
            return (
              <div 
                key={answer.question_id} 
                style={{ 
                  marginBottom: '20px', 
                  padding: '15px', 
                  backgroundColor: answer.is_correct ? '#d4edda' : '#f8d7da',
                  border: `1px solid ${answer.is_correct ? '#c3e6cb' : '#f5c6cb'}`,
                  borderRadius: '8px'
                }}
              >
                <p style={{ fontWeight: 'bold', marginBottom: '8px' }}>
                  Q{questionNumber}: {question.text}
                </p>
                
                <p style={{ marginBottom: '4px' }}>
                  <strong>Your answer:</strong> {getOptionText(question, answer.selected_answer)}
                  {answer.is_correct ? ' ✅' : ' ❌'}
                </p>
                
                {!answer.is_correct && (
                  <p style={{ marginBottom: '0', color: '#155724' }}>
                    <strong>Correct answer:</strong> {getOptionText(question, answer.correct_answer)}
                  </p>
                )}
              </div>
            );
          })}
        </div>
        
        <div style={{ marginTop: '30px' }}>
          <button className="button" onClick={onRestart}>
            Take Another Quiz
          </button>
        </div>
      </div>
    </div>
  );
};

export default ScoreDisplay;