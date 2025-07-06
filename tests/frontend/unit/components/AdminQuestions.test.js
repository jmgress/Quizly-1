import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AdminQuestions from '../../../../frontend/src/components/AdminQuestions';

// Mock axios more specifically for Jest compatibility
jest.mock('axios', () => ({
  get: jest.fn(),
  put: jest.fn(),
}));

import axios from 'axios';

// Mock question data
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
    correct_answer: 'c',
    category: 'geography'
  }
];

describe('AdminQuestions Component', () => {
  let mockOnGoHome;
  let consoleErrorSpy;

  beforeEach(() => {
    jest.clearAllMocks();
    mockOnGoHome = jest.fn();
    // Mock console.error to prevent error logs from cluttering test output
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    // Restore console.error after each test
    consoleErrorSpy.mockRestore();
  });

  it('displays loading state initially', () => {
    // Mock implementation that delays resolution to test loading state
    axios.get.mockImplementation(() => new Promise(resolve => {
      setTimeout(() => resolve({ data: mockQuestions }), 100);
    }));

    render(<AdminQuestions onGoHome={mockOnGoHome} />);

    expect(screen.getByText('Loading all questions...')).toBeInTheDocument();
  });

  it('displays error state when API call fails', async () => {
    const apiError = new Error('API Error');
    axios.get.mockRejectedValueOnce(apiError);

    render(<AdminQuestions onGoHome={mockOnGoHome} />);

    await waitFor(() => {
      expect(screen.getByText('Failed to load questions. Please try again later.')).toBeInTheDocument();
    });

    // Verify that console.error was called with the correct error
    expect(consoleErrorSpy).toHaveBeenCalledWith('Error fetching questions:', apiError);
  });

  it('loads and displays questions successfully', async () => {
    axios.get.mockResolvedValueOnce({ data: mockQuestions });

    render(<AdminQuestions onGoHome={mockOnGoHome} />);

    // Wait for questions to load
    await waitFor(() => {
      expect(screen.getByText('What is the capital of France?')).toBeInTheDocument();
    });

    // Check if API was called correctly
    expect(axios.get).toHaveBeenCalledWith('http://localhost:8000/api/questions?limit=1000');

    // Check admin header after loading
    expect(screen.getByText('🛠️ Admin: Question Management')).toBeInTheDocument();
    expect(screen.getByText('View and edit all quiz questions')).toBeInTheDocument();
    expect(screen.getByText('Back to Home')).toBeInTheDocument();

    // Check question details - look for "Total Questions:" and "1" separately
    expect(screen.getByText('Total Questions:')).toBeInTheDocument();
    expect(screen.getByText('Categories:')).toBeInTheDocument();
    expect(screen.getByText('✓ Correct')).toBeInTheDocument();
  });

  it('calls onGoHome when back button is clicked', async () => {
    axios.get.mockResolvedValueOnce({ data: mockQuestions });

    render(<AdminQuestions onGoHome={mockOnGoHome} />);

    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByText('Back to Home')).toBeInTheDocument();
    });

    const backButton = screen.getByText('Back to Home');
    fireEvent.click(backButton);

    expect(mockOnGoHome).toHaveBeenCalledTimes(1);
  });

  it('allows entering edit mode', async () => {
    axios.get.mockResolvedValueOnce({ data: mockQuestions });

    render(<AdminQuestions onGoHome={mockOnGoHome} />);

    await waitFor(() => {
      expect(screen.getByText('What is the capital of France?')).toBeInTheDocument();
    });

    // Click edit button 
    const editButton = screen.getByText('Edit');
    fireEvent.click(editButton);

    // Check if edit form appears
    await waitFor(() => {
      expect(screen.getByDisplayValue('What is the capital of France?')).toBeInTheDocument();
      expect(screen.getByDisplayValue('geography')).toBeInTheDocument();
      expect(screen.getByText('Save')).toBeInTheDocument();
      expect(screen.getByText('Cancel')).toBeInTheDocument();
    });
  });
});