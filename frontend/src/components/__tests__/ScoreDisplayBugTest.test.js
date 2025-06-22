import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ScoreDisplay from '../ScoreDisplay';

// Test data that simulates the exact scenario that causes the bug
const mockQuestionsWithMismatch = [
  {
    id: 3,
    text: 'What is 2 + 2?',
    options: [
      { id: 'a', text: '3' },
      { id: 'b', text: '4' },
      { id: 'c', text: '5' },
      { id: 'd', text: '6' }
    ],
    correct_answer: 'b'
  },
  {
    id: 5,
    text: 'What is the largest ocean on Earth?',
    options: [
      { id: 'a', text: 'Atlantic Ocean' },
      { id: 'b', text: 'Indian Ocean' },
      { id: 'c', text: 'Arctic Ocean' },
      { id: 'd', text: 'Pacific Ocean' }
    ],
    correct_answer: 'd'
  }
];

// This simulates the backend response with mixed correct/incorrect answers
const mockResultsWithMismatch = {
  correct_answers: 1,
  total_questions: 2,
  score_percentage: 50,
  answers: [
    {
      question_id: 3,      // This was answered incorrectly
      selected_answer: 'a',
      correct_answer: 'b',
      is_correct: false
    },
    {
      question_id: 5,      // This was answered correctly  
      selected_answer: 'd',
      correct_answer: 'd',
      is_correct: true
    }
  ]
};

describe('ScoreDisplay Bug Reproduction', () => {
  let mockOnRestart;

  beforeEach(() => {
    mockOnRestart = jest.fn();
  });

  test('displays correct/incorrect indicators properly', () => {
    render(
      <ScoreDisplay
        results={mockResultsWithMismatch}
        questions={mockQuestionsWithMismatch}
        onRestart={mockOnRestart}
      />
    );

    // Check that score summary is correct
    expect(screen.getByText('1/2')).toBeInTheDocument();
    expect(screen.getByText('50% Correct')).toBeInTheDocument();

    // Check individual answer displays
    // First question (incorrect answer)
    expect(screen.getByText(/What is 2 \+ 2\?/)).toBeInTheDocument();
    expect(screen.getByText('Your answer:')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('❌')).toBeInTheDocument();
    expect(screen.getByText(/Correct answer:.*4/)).toBeInTheDocument();

    // Second question (correct answer)
    expect(screen.getByText(/What is the largest ocean on Earth\?/)).toBeInTheDocument();
    expect(screen.getByText('Pacific Ocean')).toBeInTheDocument();
    expect(screen.getByText('✅')).toBeInTheDocument();
    
    // Make sure "Correct answer:" doesn't appear for the correct answer
    const correctAnswerTexts = screen.getAllByText(/Correct answer:/);
    expect(correctAnswerTexts).toHaveLength(1); // Only for the incorrect answer
  });

  test('question numbering matches display order', () => {
    render(
      <ScoreDisplay
        results={mockResultsWithMismatch}
        questions={mockQuestionsWithMismatch}
        onRestart={mockOnRestart}
      />
    );

    // The current implementation numbers questions by their order in results.answers array
    // This test will reveal if there's a mismatch between the question numbering and content
    expect(screen.getByText(/Q1:.*What is 2 \+ 2\?/)).toBeInTheDocument();
    expect(screen.getByText(/Q2:.*What is the largest ocean on Earth\?/)).toBeInTheDocument();
  });
});