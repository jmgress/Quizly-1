import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ScoreDisplay from '../../../../../frontend/src/components/ScoreDisplay';

// Mock data for testing
const mockQuestions = [
  {
    id: 1,
    text: 'What is the capital of France?',
    options: [
      { id: 'a', text: 'London' },
      { id: 'b', text: 'Berlin' },
      { id: 'c', text: 'Paris' },
      { id: 'd', text: 'Madrid' }
    ],
    correct_answer: 'c'
  },
  {
    id: 2,
    text: 'What is 2 + 2?',
    options: [
      { id: 'a', text: '3' },
      { id: 'b', text: '4' },
      { id: 'c', text: '5' },
      { id: 'd', text: '6' }
    ],
    correct_answer: 'b'
  }
];

const mockResultsHighScore = {
  correct_answers: 2,
  total_questions: 2,
  score_percentage: 100,
  answers: [
    {
      question_id: 1,
      selected_answer: 'c',
      correct_answer: 'c',
      is_correct: true
    },
    {
      question_id: 2,
      selected_answer: 'b',
      correct_answer: 'b',
      is_correct: true
    }
  ]
};

const mockResultsLowScore = {
  correct_answers: 1,
  total_questions: 2,
  score_percentage: 50,
  answers: [
    {
      question_id: 1,
      selected_answer: 'a',
      correct_answer: 'c',
      is_correct: false
    },
    {
      question_id: 2,
      selected_answer: 'b',
      correct_answer: 'b',
      is_correct: true
    }
  ]
};

const mockResultsVeryLowScore = {
  correct_answers: 0,
  total_questions: 2,
  score_percentage: 0,
  answers: [
    {
      question_id: 1,
      selected_answer: 'a',
      correct_answer: 'c',
      is_correct: false
    },
    {
      question_id: 2,
      selected_answer: 'a',
      correct_answer: 'b',
      is_correct: false
    }
  ]
};

describe('ScoreDisplay Component', () => {
  let mockOnRestart;

  beforeEach(() => {
    mockOnRestart = jest.fn();
  });

  test('displays the correct score based on props - high score', () => {
    render(
      <ScoreDisplay
        results={mockResultsHighScore}
        questions={mockQuestions}
        onRestart={mockOnRestart}
      />
    );

    // Check score display
    expect(screen.getByText('2/2')).toBeInTheDocument();
    expect(screen.getByText('100% Correct')).toBeInTheDocument();
    expect(screen.getByText("🏆 Excellent! You're a quiz master!")).toBeInTheDocument();
  });

  test('displays the correct score based on props - medium score', () => {
    render(
      <ScoreDisplay
        results={mockResultsLowScore}
        questions={mockQuestions}
        onRestart={mockOnRestart}
      />
    );

    // Check score display
    expect(screen.getByText('1/2')).toBeInTheDocument();
    expect(screen.getByText('50% Correct')).toBeInTheDocument();
    expect(screen.getByText('👍 Good effort! Keep practicing!')).toBeInTheDocument();
  });

  test('displays the correct score based on props - low score', () => {
    render(
      <ScoreDisplay
        results={mockResultsVeryLowScore}
        questions={mockQuestions}
        onRestart={mockOnRestart}
      />
    );

    // Check score display
    expect(screen.getByText('0/2')).toBeInTheDocument();
    expect(screen.getByText('0% Correct')).toBeInTheDocument();
    expect(screen.getByText('📚 Keep studying and try again!')).toBeInTheDocument();
  });

  test('calls onRestart when restart button is clicked', () => {
    render(
      <ScoreDisplay
        results={mockResultsHighScore}
        questions={mockQuestions}
        onRestart={mockOnRestart}
      />
    );

    const restartButton = screen.getByText('Take Another Quiz');
    fireEvent.click(restartButton);

    expect(mockOnRestart).toHaveBeenCalledTimes(1);
  });

  test('displays correct answer review for correct answers', () => {
    render(
      <ScoreDisplay
        results={mockResultsHighScore}
        questions={mockQuestions}
        onRestart={mockOnRestart}
      />
    );

    // Check that questions are displayed
    expect(screen.getByText(/Q1:/)).toBeInTheDocument();
    expect(screen.getByText(/What is the capital of France?/)).toBeInTheDocument();
    expect(screen.getByText(/Q2:/)).toBeInTheDocument();
    expect(screen.getByText(/What is 2 \+ 2?/)).toBeInTheDocument();
    
    // Check that "Your answer:" text appears
    const yourAnswerTexts = screen.getAllByText(/Your answer:/);
    expect(yourAnswerTexts).toHaveLength(2);
  });

  test('displays correct answer review for incorrect answers', () => {
    render(
      <ScoreDisplay
        results={mockResultsLowScore}
        questions={mockQuestions}
        onRestart={mockOnRestart}
      />
    );

    // Check that questions are displayed
    expect(screen.getByText(/Q1:/)).toBeInTheDocument();
    expect(screen.getByText(/What is the capital of France?/)).toBeInTheDocument();
    expect(screen.getByText(/Q2:/)).toBeInTheDocument();
    expect(screen.getByText(/What is 2 \+ 2?/)).toBeInTheDocument();
    
    // Check that "Correct answer:" text appears for incorrect answers
    expect(screen.getByText(/Correct answer:/)).toBeInTheDocument();
    
    // Check that both "Your answer:" appear
    const yourAnswerTexts = screen.getAllByText(/Your answer:/);
    expect(yourAnswerTexts).toHaveLength(2);
  });

  test('renders quiz complete title', () => {
    render(
      <ScoreDisplay
        results={mockResultsHighScore}
        questions={mockQuestions}
        onRestart={mockOnRestart}
      />
    );

    expect(screen.getByText('🎯 Quiz Complete!')).toBeInTheDocument();
    expect(screen.getByText('📋 Review Your Answers:')).toBeInTheDocument();
  });

  test('matches snapshot for different score values - high score', () => {
    const { container } = render(
      <ScoreDisplay
        results={mockResultsHighScore}
        questions={mockQuestions}
        onRestart={mockOnRestart}
      />
    );
    expect(container.firstChild).toMatchSnapshot();
  });

  test('matches snapshot for different score values - low score', () => {
    const { container } = render(
      <ScoreDisplay
        results={mockResultsVeryLowScore}
        questions={mockQuestions}
        onRestart={mockOnRestart}
      />
    );
    expect(container.firstChild).toMatchSnapshot();
  });

  test('displays different score messages based on percentage', () => {
    const mockResults90 = { ...mockResultsHighScore, score_percentage: 95 };
    const mockResults75 = { ...mockResultsHighScore, score_percentage: 75 };
    const mockResults55 = { ...mockResultsHighScore, score_percentage: 55 };
    const mockResults25 = { ...mockResultsHighScore, score_percentage: 25 };

    // Test excellent message (≥90%)
    const { rerender } = render(
      <ScoreDisplay
        results={mockResults90}
        questions={mockQuestions}
        onRestart={mockOnRestart}
      />
    );
    expect(screen.getByText("🏆 Excellent! You're a quiz master!")).toBeInTheDocument();

    // Test great job message (≥70%)
    rerender(
      <ScoreDisplay
        results={mockResults75}
        questions={mockQuestions}
        onRestart={mockOnRestart}
      />
    );
    expect(screen.getByText('🎉 Great job! Well done!')).toBeInTheDocument();

    // Test good effort message (≥50%)
    rerender(
      <ScoreDisplay
        results={mockResults55}
        questions={mockQuestions}
        onRestart={mockOnRestart}
      />
    );
    expect(screen.getByText('👍 Good effort! Keep practicing!')).toBeInTheDocument();

    // Test keep studying message (<50%)
    rerender(
      <ScoreDisplay
        results={mockResults25}
        questions={mockQuestions}
        onRestart={mockOnRestart}
      />
    );
    expect(screen.getByText('📚 Keep studying and try again!')).toBeInTheDocument();
  });
});