import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Quiz from '../../../../frontend/src/components/Quiz';

// Mock axios
jest.mock('axios', () => ({
  get: jest.fn(),
  post: jest.fn(),
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
    correct_answer: 'b',
    category: 'math'
  }
];

describe('Quiz Component', () => {
  let mockOnRestart;

  beforeEach(() => {
    jest.clearAllMocks();
    mockOnRestart = jest.fn();
  });

  it('displays loading state initially', () => {
    axios.get.mockImplementation(() => new Promise(() => {})); // Never resolves

    render(<Quiz onRestart={mockOnRestart} category="geography" source="database" />);

    expect(screen.getByText('Loading geography questions...')).toBeInTheDocument();
  });

  it('displays error state when API call fails', async () => {
    axios.get.mockRejectedValueOnce(new Error('API Error'));

    render(<Quiz onRestart={mockOnRestart} category="geography" source="database" />);

    await waitFor(() => {
      expect(screen.getByText('Failed to load questions. Please try again later.')).toBeInTheDocument();
    });
  });

  it('loads and displays questions from database', async () => {
    axios.get.mockResolvedValueOnce({ data: mockQuestions });

    render(<Quiz onRestart={mockOnRestart} category="geography" source="database" />);

    await waitFor(() => {
      expect(screen.getByText('What is the capital of France?')).toBeInTheDocument();
    });

    // Check if API was called with correct URL for database questions
    expect(axios.get).toHaveBeenCalledWith('http://localhost:8000/api/questions?category=geography&limit=10');
  });

  it('loads and displays AI-generated questions', async () => {
    axios.get.mockResolvedValueOnce({ data: mockQuestions });

    render(<Quiz onRestart={mockOnRestart} category="geography" source="ai" model="llama3.2" />);

    await waitFor(() => {
      expect(screen.getByText('What is the capital of France?')).toBeInTheDocument();
    });

    // Check if API was called with correct URL for AI questions
    expect(axios.get).toHaveBeenCalledWith('http://localhost:8000/api/questions/ai?subject=geography&limit=5&model=llama3.2');
  });

  it('progresses through questions when answers are selected', async () => {
    axios.get.mockResolvedValueOnce({ data: mockQuestions });

    render(<Quiz onRestart={mockOnRestart} category="geography" source="database" />);

    await waitFor(() => {
      expect(screen.getByText('What is the capital of France?')).toBeInTheDocument();
    });

    // Select an answer
    const parisOption = screen.getByText('Paris');
    fireEvent.click(parisOption);

    // Submit the answer
    const submitButton = screen.getByText('Submit Answer');
    fireEvent.click(submitButton);

    // Should show feedback
    await waitFor(() => {
      expect(screen.getByText('🎉 Correct! Well done!')).toBeInTheDocument();
    });

    // Wait for auto-advance to next question (2 second delay)
    await waitFor(() => {
      expect(screen.getByText('What is 2 + 2?')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('shows score display when quiz is complete', async () => {
    axios.get.mockResolvedValueOnce({ data: [mockQuestions[0]] }); // Only one question
    axios.post.mockResolvedValueOnce({ 
      data: { 
        score: 100, 
        correct: 1, 
        total: 1,
        answers: [
          {
            question_id: 1,
            selected_answer: 'c',
            correct_answer: 'c'
          }
        ]
      } 
    });

    render(<Quiz onRestart={mockOnRestart} category="geography" source="database" />);

    await waitFor(() => {
      expect(screen.getByText('What is the capital of France?')).toBeInTheDocument();
    });

    // Select correct answer
    const parisOption = screen.getByText('Paris');
    fireEvent.click(parisOption);

    // Submit answer (quiz completes automatically after 2 seconds)
    const submitButton = screen.getByText('Submit Answer');
    fireEvent.click(submitButton);

    // Should show score display after auto-completion
    await waitFor(() => {
      expect(screen.getByText('🎯 Quiz Complete!')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('displays AI error message for AI source failures', async () => {
    axios.get.mockRejectedValueOnce(new Error('AI Error'));

    render(<Quiz onRestart={mockOnRestart} category="geography" source="ai" />);

    await waitFor(() => {
      expect(screen.getByText(/Failed to generate AI questions/)).toBeInTheDocument();
      expect(screen.getByText(/Please ensure Ollama is running/)).toBeInTheDocument();
    });
  });
});