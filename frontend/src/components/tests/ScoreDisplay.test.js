import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ScoreDisplay from '../ScoreDisplay';

const mockResults = (score) => ({
  correct_answers: score,
  total_questions: 5,
  score_percentage: (score / 5) * 100,
  answers: []
});

const questions = [
  { id: 1, text: 'Question 1', options: [{ id: 'a', text: 'A' }], correct_answer: 'a' }
];

test('displays the correct score based on props', () => {
  const results = mockResults(3);
  render(<ScoreDisplay results={results} questions={questions} onRestart={() => {}} />);
  expect(screen.getByText('3/5')).toBeInTheDocument();
  expect(screen.getByText(/60% Correct/)).toBeInTheDocument();
});

test('matches snapshot for different score values', () => {
  const { asFragment } = render(
    <ScoreDisplay results={mockResults(5)} questions={questions} onRestart={() => {}} />
  );
  expect(asFragment()).toMatchSnapshot();
});
