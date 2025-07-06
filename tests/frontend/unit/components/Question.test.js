import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Question from '../Question';

// Mock question data for testing
const mockQuestion = {
  id: 1,
  text: 'What is the capital of France?',
  options: [
    { id: 'a', text: 'London' },
    { id: 'b', text: 'Berlin' },
    { id: 'c', text: 'Paris' },
    { id: 'd', text: 'Madrid' }
  ],
  correct_answer: 'c'
};

describe('Question Component', () => {
  let mockOnAnswerSelect;

  beforeEach(() => {
    mockOnAnswerSelect = jest.fn();
  });

  test('renders question text and choices', () => {
    render(
      <Question
        question={mockQuestion}
        onAnswerSelect={mockOnAnswerSelect}
        selectedAnswer={null}
        showFeedback={false}
        disabled={false}
      />
    );

    // Check that question text is rendered
    expect(screen.getByText('What is the capital of France?')).toBeInTheDocument();

    // Check that all options are rendered
    expect(screen.getByText('London')).toBeInTheDocument();
    expect(screen.getByText('Berlin')).toBeInTheDocument();
    expect(screen.getByText('Paris')).toBeInTheDocument();
    expect(screen.getByText('Madrid')).toBeInTheDocument();

    // Check that all options are rendered as buttons
    const buttons = screen.getAllByRole('button');
    expect(buttons).toHaveLength(4);
  });

  test('invokes callback when an answer is selected', () => {
    render(
      <Question
        question={mockQuestion}
        onAnswerSelect={mockOnAnswerSelect}
        selectedAnswer={null}
        showFeedback={false}
        disabled={false}
      />
    );

    // Click on the "Paris" option
    const parisButton = screen.getByText('Paris');
    fireEvent.click(parisButton);

    // Check that callback was called with correct parameters
    expect(mockOnAnswerSelect).toHaveBeenCalledTimes(1);
    expect(mockOnAnswerSelect).toHaveBeenCalledWith(1, 'c');
  });

  test('does not invoke callback when disabled', () => {
    render(
      <Question
        question={mockQuestion}
        onAnswerSelect={mockOnAnswerSelect}
        selectedAnswer={null}
        showFeedback={false}
        disabled={true}
      />
    );

    // Click on the "Paris" option
    const parisButton = screen.getByText('Paris');
    fireEvent.click(parisButton);

    // Check that callback was not called
    expect(mockOnAnswerSelect).not.toHaveBeenCalled();
  });

  test('applies selected class to selected answer', () => {
    render(
      <Question
        question={mockQuestion}
        onAnswerSelect={mockOnAnswerSelect}
        selectedAnswer="c"
        showFeedback={false}
        disabled={false}
      />
    );

    const parisButton = screen.getByText('Paris');
    expect(parisButton).toHaveClass('option-button', 'selected');
  });

  test('shows correct feedback when answer is correct', () => {
    render(
      <Question
        question={mockQuestion}
        onAnswerSelect={mockOnAnswerSelect}
        selectedAnswer="c"
        showFeedback={true}
        disabled={false}
      />
    );

    // Check feedback message
    expect(screen.getByText('🎉 Correct! Well done!')).toBeInTheDocument();

    // Check that correct answer has correct class
    const parisButton = screen.getByText('Paris');
    expect(parisButton).toHaveClass('option-button', 'selected', 'correct');
  });

  test('shows incorrect feedback when answer is wrong', () => {
    render(
      <Question
        question={mockQuestion}
        onAnswerSelect={mockOnAnswerSelect}
        selectedAnswer="a"
        showFeedback={true}
        disabled={false}
      />
    );

    // Check feedback message shows correct answer
    expect(screen.getByText('❌ Incorrect. The correct answer is: Paris')).toBeInTheDocument();

    // Check that incorrect answer has incorrect class
    const londonButton = screen.getByText('London');
    expect(londonButton).toHaveClass('option-button', 'selected', 'incorrect');

    // Check that correct answer has correct class
    const parisButton = screen.getByText('Paris');
    expect(parisButton).toHaveClass('option-button', 'correct');
  });
});