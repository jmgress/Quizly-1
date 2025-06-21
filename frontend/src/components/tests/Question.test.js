import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Question from '../Question';

const sampleQuestion = {
  id: 1,
  text: 'What is the capital of France?',
  correct_answer: 'c',
  options: [
    { id: 'a', text: 'London' },
    { id: 'b', text: 'Berlin' },
    { id: 'c', text: 'Paris' }
  ]
};

test('renders question text and choices', () => {
  render(
    <Question
      question={sampleQuestion}
      selectedAnswer={null}
      onAnswerSelect={() => {}}
      showFeedback={false}
      disabled={false}
    />
  );

  expect(screen.getByText('What is the capital of France?')).toBeInTheDocument();
  expect(screen.getByText('London')).toBeInTheDocument();
  expect(screen.getByText('Berlin')).toBeInTheDocument();
  expect(screen.getByText('Paris')).toBeInTheDocument();
});

test('invokes callback when an answer is selected', () => {
  const mockSelect = jest.fn();

  render(
    <Question
      question={sampleQuestion}
      selectedAnswer={null}
      onAnswerSelect={mockSelect}
      showFeedback={false}
      disabled={false}
    />
  );

  fireEvent.click(screen.getByText('Paris'));
  expect(mockSelect).toHaveBeenCalledWith(1, 'c');
});
