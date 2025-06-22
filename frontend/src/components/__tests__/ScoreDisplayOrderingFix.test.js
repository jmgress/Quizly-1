import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ScoreDisplay from '../ScoreDisplay';

describe('ScoreDisplay Question Ordering Fix', () => {
  test('displays questions in original quiz order, not results order', () => {
    // This test verifies the fix for the issue where questions might
    // appear in wrong order in the results screen
    
    const originalQuestions = [
      {
        id: 100,
        text: 'First Question Shown',
        options: [
          { id: 'a', text: 'Answer A' },
          { id: 'b', text: 'Answer B' }
        ],
        correct_answer: 'a'
      },
      {
        id: 200,
        text: 'Second Question Shown',
        options: [
          { id: 'a', text: 'Answer C' },
          { id: 'b', text: 'Answer D' }
        ],
        correct_answer: 'b'
      }
    ];

    const resultsInDifferentOrder = {
      correct_answers: 1,
      total_questions: 2,
      score_percentage: 50,
      answers: [
        {
          question_id: 200,  // Second question appears first in results
          selected_answer: 'b',
          correct_answer: 'b',
          is_correct: true
        },
        {
          question_id: 100,  // First question appears second in results
          selected_answer: 'b',
          correct_answer: 'a',
          is_correct: false
        }
      ]
    };

    render(
      <ScoreDisplay
        results={resultsInDifferentOrder}
        questions={originalQuestions}
        onRestart={() => {}}
      />
    );

    // Questions should be displayed in original order (100, 200)
    // not in results order (200, 100)
    expect(screen.getByText(/Q1.*First Question Shown/)).toBeInTheDocument();
    expect(screen.getByText(/Q2.*Second Question Shown/)).toBeInTheDocument();

    // Verify score is displayed correctly
    expect(screen.getByText('1/2')).toBeInTheDocument();
    expect(screen.getByText('50% Correct')).toBeInTheDocument();
  });

  test('handles missing questions gracefully while maintaining order', () => {
    const questions = [
      {
        id: 1,
        text: 'Question 1',
        options: [{ id: 'a', text: 'Option A' }],
        correct_answer: 'a'
      },
      {
        id: 3,
        text: 'Question 3',
        options: [{ id: 'a', text: 'Option A' }],
        correct_answer: 'a'
      }
    ];

    const results = {
      correct_answers: 1,
      total_questions: 2,
      score_percentage: 50,
      answers: [
        {
          question_id: 3,  // This exists
          selected_answer: 'a',
          correct_answer: 'a',
          is_correct: true
        },
        {
          question_id: 2,  // This doesn't exist in questions array
          selected_answer: 'a',
          correct_answer: 'a',
          is_correct: false
        },
        {
          question_id: 1,  // This exists
          selected_answer: 'a',
          correct_answer: 'a',
          is_correct: true
        }
      ]
    };

    render(
      <ScoreDisplay
        results={results}
        questions={questions}
        onRestart={() => {}}
      />
    );

    // Should show Q1 for question id 1 and Q2 for question id 3
    // Question id 2 should be skipped since it doesn't exist
    expect(screen.getByText(/Q1.*Question 1/)).toBeInTheDocument();
    expect(screen.getByText(/Q2.*Question 3/)).toBeInTheDocument();
    
    // Should not show a Q? for the missing question
    expect(screen.queryByText(/Q\?/)).not.toBeInTheDocument();
  });
});