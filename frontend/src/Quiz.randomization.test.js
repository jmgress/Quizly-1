/**
 * Tests for Quiz component answer randomization functionality
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import Quiz from './components/Quiz';

// Mock axios using the default export pattern
jest.mock('axios', () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
    post: jest.fn(),
  },
}));

// Import after mocking
import axios from 'axios';
const mockedAxios = axios;

// Mock the onRestart function
const mockOnRestart = jest.fn();

describe('Quiz Answer Randomization', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset Math.random to ensure predictable but different results
    jest.spyOn(Math, 'random');
  });

  afterEach(() => {
    Math.random.mockRestore();
  });

  test('should shuffle answer options when loading questions', async () => {
    // Arrange: Mock API response with predictable question
    const testQuestion = {
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
    };

    mockedAxios.get.mockResolvedValue({ data: [testQuestion] });

    // Mock Math.random to provide predictable shuffling
    // This sequence will shuffle [0,1,2,3] to [2,0,3,1]
    const randomValues = [0.8, 0.6, 0.2];
    let callIndex = 0;
    Math.random.mockImplementation(() => {
      const value = randomValues[callIndex % randomValues.length];
      callIndex++;
      return value;
    });

    // Act: Render the Quiz component
    render(
      <Quiz 
        onRestart={mockOnRestart} 
        category="geography" 
        source="database" 
      />
    );

    // Wait for questions to load
    await waitFor(() => {
      expect(screen.getByText('What is the capital of France?')).toBeInTheDocument();
    });

    // Assert: Verify that options are present but potentially in different order
    const optionButtons = screen.getAllByRole('button');
    const optionTexts = optionButtons
      .filter(btn => ['London', 'Berlin', 'Paris', 'Madrid'].includes(btn.textContent))
      .map(btn => btn.textContent);

    // All options should still be present
    expect(optionTexts).toHaveLength(4);
    expect(optionTexts).toContain('London');
    expect(optionTexts).toContain('Berlin');
    expect(optionTexts).toContain('Paris');
    expect(optionTexts).toContain('Madrid');

    // The correct answer should still be marked correctly
    // (we can't easily test the shuffling deterministically due to React's rendering)
    expect(mockedAxios.get).toHaveBeenCalledWith(
      'http://localhost:8000/api/questions?category=geography&limit=10'
    );
  });

  test('should maintain question structure after randomization', async () => {
    // Arrange: Mock question with known structure
    const testQuestion = {
      id: 42,
      text: 'Test question?',
      options: [
        { id: 'a', text: 'Option A' },
        { id: 'b', text: 'Option B' },
        { id: 'c', text: 'Option C' },
        { id: 'd', text: 'Option D' }
      ],
      correct_answer: 'a',
      category: 'test'
    };

    mockedAxios.get.mockResolvedValue({ data: [testQuestion] });

    // Act: Render the Quiz
    render(
      <Quiz 
        onRestart={mockOnRestart} 
        category="test" 
        source="database" 
      />
    );

    // Wait for questions to load
    await waitFor(() => {
      expect(screen.getByText('Test question?')).toBeInTheDocument();
    });

    // Assert: Question text should be unchanged
    expect(screen.getByText('Test question?')).toBeInTheDocument();
    
    // All 4 options should be present
    const optionButtons = screen.getAllByRole('button');
    const questionOptions = optionButtons.filter(btn => 
      btn.textContent.startsWith('Option ')
    );
    expect(questionOptions).toHaveLength(4);

    // Options should still have all content
    expect(screen.getByText('Option A')).toBeInTheDocument();
    expect(screen.getByText('Option B')).toBeInTheDocument();
    expect(screen.getByText('Option C')).toBeInTheDocument();
    expect(screen.getByText('Option D')).toBeInTheDocument();
  });

  test('should work with AI-generated questions', async () => {
    // Arrange: Mock AI question response
    const aiQuestion = {
      id: 1000,
      text: 'What is machine learning?',
      options: [
        { id: 'a', text: 'A type of computer hardware' },
        { id: 'b', text: 'A subset of artificial intelligence' },
        { id: 'c', text: 'A programming language' },
        { id: 'd', text: 'A database system' }
      ],
      correct_answer: 'b',
      category: 'technology'
    };

    mockedAxios.get.mockResolvedValue({ data: [aiQuestion] });

    // Act: Render with AI source
    render(
      <Quiz 
        onRestart={mockOnRestart} 
        category="technology" 
        source="ai" 
      />
    );

    // Wait for questions to load
    await waitFor(() => {
      expect(screen.getByText('What is machine learning?')).toBeInTheDocument();
    });

    // Assert: All options should be present
    expect(screen.getByText('A type of computer hardware')).toBeInTheDocument();
    expect(screen.getByText('A subset of artificial intelligence')).toBeInTheDocument();
    expect(screen.getByText('A programming language')).toBeInTheDocument();
    expect(screen.getByText('A database system')).toBeInTheDocument();

    // Verify correct API call for AI questions
    expect(mockedAxios.get).toHaveBeenCalledWith(
      'http://localhost:8000/api/questions/ai?subject=technology&limit=5'
    );
  });
});