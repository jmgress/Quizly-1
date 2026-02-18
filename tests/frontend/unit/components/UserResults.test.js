import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import UserResults from '../../../../frontend/src/components/UserResults';

// Mock axios
jest.mock('axios');

const mockSessions = [
  {
    id: 'id1',
    total_questions: 10,
    correct_answers: 8,
    score_percentage: 80.0,
    created_at: '2023-01-01T10:00:00',
    answers: []
  },
  {
    id: 'id2',
    total_questions: 5,
    correct_answers: 5,
    score_percentage: 100.0,
    created_at: '2023-01-02T10:00:00',
    answers: []
  }
];

describe('UserResults Component', () => {
  test('renders loading state initially', () => {
    // Return a promise that never resolves to test loading state
    axios.get.mockImplementation(() => new Promise(() => {}));

    render(<UserResults />);
    expect(screen.getByText('Loading results...')).toBeInTheDocument();
  });

  test('renders sessions table after fetching data', async () => {
    axios.get.mockResolvedValue({ data: mockSessions });

    render(<UserResults />);

    await waitFor(() => {
      expect(screen.queryByText('Loading results...')).not.toBeInTheDocument();
    });

    expect(screen.getByText('Total Sessions:')).toBeInTheDocument();
    // Check for some content from mockSessions
    expect(screen.getByText('80.0%')).toBeInTheDocument();
    expect(screen.getByText('100.0%')).toBeInTheDocument();

    expect(screen.getByText('8 / 10')).toBeInTheDocument();
    expect(screen.getByText('5 / 5')).toBeInTheDocument();
  });

  test('renders error message on fetch failure', async () => {
    axios.get.mockRejectedValue(new Error('Network Error'));

    render(<UserResults />);

    await waitFor(() => {
      expect(screen.getByText('Failed to load quiz sessions. Please try again later.')).toBeInTheDocument();
    });

    expect(screen.getByText('Try Again')).toBeInTheDocument();
  });
});
