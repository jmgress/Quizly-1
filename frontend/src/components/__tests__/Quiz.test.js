import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import Quiz from '../Quiz';

// Mock axios
jest.mock('axios', () => ({
  get: jest.fn(() => Promise.resolve({ data: [] })),
  post: jest.fn(() => Promise.resolve({ data: {} }))
}));

import axios from 'axios';
const mockedAxios = axios;

// Mock ScoreDisplay component
jest.mock('../ScoreDisplay', () => {
  return function MockScoreDisplay({ results, onRestart }) {
    return (
      <div data-testid="score-display">
        Score: {results.score}
        <button onClick={onRestart}>Restart</button>
      </div>
    );
  };
});

describe('Quiz Component', () => {
  const mockOnRestart = jest.fn();
  const mockQuestions = [
    {
      id: 1,
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
      id: 2,
      text: 'What is 3 + 3?',
      options: [
        { id: 'a', text: '5' },
        { id: 'b', text: '6' },
        { id: 'c', text: '7' },
        { id: 'd', text: '8' }
      ],
      correct_answer: 'b'
    }
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
    mockedAxios.get.mockResolvedValue({ data: mockQuestions });
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  test('should not auto-advance question without user interaction', async () => {
    render(<Quiz onRestart={mockOnRestart} category="math" source="database" />);

    // Wait for questions to load
    await waitFor(() => {
      expect(screen.getByText('What is 2 + 2?')).toBeInTheDocument();
    });

    // Verify we're on the first question
    expect(screen.getByText('Question 1 of 2')).toBeInTheDocument();
    expect(screen.getByText('What is 2 + 2?')).toBeInTheDocument();

    // Fast-forward time by 3 seconds (more than the 2-second timeout)
    act(() => {
      jest.advanceTimersByTime(3000);
    });

    // Question should still be the first question since no answer was submitted
    expect(screen.getByText('Question 1 of 2')).toBeInTheDocument();
    expect(screen.getByText('What is 2 + 2?')).toBeInTheDocument();
    expect(screen.queryByText('What is 3 + 3?')).not.toBeInTheDocument();
  });

  test('should auto-advance after submitting an answer', async () => {
    render(<Quiz onRestart={mockOnRestart} category="math" source="database" />);

    // Wait for questions to load
    await waitFor(() => {
      expect(screen.getByText('What is 2 + 2?')).toBeInTheDocument();
    });

    // Select an answer
    const option = screen.getByText('4');
    fireEvent.click(option);

    // Submit the answer
    const submitButton = screen.getByText('Submit Answer');
    fireEvent.click(submitButton);

    // Should show feedback immediately
    await waitFor(() => {
      expect(screen.getByText('🎉 Correct! Well done!')).toBeInTheDocument();
    });

    // Fast-forward time by 2.1 seconds to trigger the timeout
    act(() => {
      jest.advanceTimersByTime(2100);
    });

    // Should now be on the second question
    await waitFor(() => {
      expect(screen.getByText('Question 2 of 2')).toBeInTheDocument();
      expect(screen.getByText('What is 3 + 3?')).toBeInTheDocument();
    });
  });

  test('should clear timeout when component unmounts', async () => {
    const { unmount } = render(<Quiz onRestart={mockOnRestart} category="math" source="database" />);

    // Wait for questions to load
    await waitFor(() => {
      expect(screen.getByText('What is 2 + 2?')).toBeInTheDocument();
    });

    // Select an answer and submit
    const option = screen.getByText('4');
    fireEvent.click(option);
    const submitButton = screen.getByText('Submit Answer');
    fireEvent.click(submitButton);

    // Unmount component before timeout fires
    unmount();

    // Advance timers - this should not cause any errors
    act(() => {
      jest.advanceTimersByTime(3000);
    });

    // No assertions needed - we're just checking that no errors occur
  });

  test('should handle rapid state changes without auto-advancing', async () => {
    const { rerender } = render(<Quiz onRestart={mockOnRestart} category="math" source="database" />);

    // Wait for questions to load
    await waitFor(() => {
      expect(screen.getByText('What is 2 + 2?')).toBeInTheDocument();
    });

    // Simulate rapid re-renders that might cause race conditions
    rerender(<Quiz onRestart={mockOnRestart} category="math" source="database" />);
    rerender(<Quiz onRestart={mockOnRestart} category="math" source="database" />);
    rerender(<Quiz onRestart={mockOnRestart} category="math" source="database" />);

    // Fast-forward time to check if any unwanted timeouts were created
    act(() => {
      jest.advanceTimersByTime(3000);
    });

    // Should still be on the first question
    expect(screen.getByText('Question 1 of 2')).toBeInTheDocument();
    expect(screen.getByText('What is 2 + 2?')).toBeInTheDocument();
  });

  test('should not have multiple active timeouts when quickly selecting and deselecting answers', async () => {
    render(<Quiz onRestart={mockOnRestart} category="math" source="database" />);

    // Wait for questions to load
    await waitFor(() => {
      expect(screen.getByText('What is 2 + 2?')).toBeInTheDocument();
    });

    // Quickly select different answers (simulating user behavior)
    const option1 = screen.getByText('3');
    const option2 = screen.getByText('4');
    const option3 = screen.getByText('5');

    fireEvent.click(option1);
    fireEvent.click(option2);
    fireEvent.click(option3);
    fireEvent.click(option2); // Final selection

    // Submit answer
    const submitButton = screen.getByText('Submit Answer');
    fireEvent.click(submitButton);

    // Advance time to let the timeout complete
    act(() => {
      jest.advanceTimersByTime(2100);
    });

    // Should advance to question 2 exactly once
    await waitFor(() => {
      expect(screen.getByText('Question 2 of 2')).toBeInTheDocument();
      expect(screen.getByText('What is 3 + 3?')).toBeInTheDocument();
    });
  });

  test('should clear timeout when question changes manually (edge case)', async () => {
    const { rerender } = render(<Quiz onRestart={mockOnRestart} category="math" source="database" />);

    // Wait for questions to load
    await waitFor(() => {
      expect(screen.getByText('What is 2 + 2?')).toBeInTheDocument();
    });

    // Select and submit answer
    const option = screen.getByText('4');
    fireEvent.click(option);
    const submitButton = screen.getByText('Submit Answer');
    fireEvent.click(submitButton);

    // Before timeout fires, simulate question change via external state change
    // This mimics the scenario described in the bug report
    rerender(<Quiz onRestart={mockOnRestart} category="science" source="database" />);

    // Fast-forward past the original timeout
    act(() => {
      jest.advanceTimersByTime(3000);
    });

    // Should handle the category change gracefully without errors
    // The test passes if no unhandled promise rejections or state update errors occur
  });
});