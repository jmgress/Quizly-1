import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import SubjectSelection from '../SubjectSelection';

// Mock axios
jest.mock('axios', () => ({
  get: jest.fn(() => Promise.resolve({ data: {} }))
}));

import axios from 'axios';
const mockedAxios = axios;

// Setup proper API mocking
const setupAPIMocks = (categories = ['geography'], models = {}, defaults = {}) => {
  mockedAxios.get.mockImplementation((url) => {
    if (url.includes('/api/categories')) {
      return Promise.resolve({ data: { categories } });
    }
    if (url.includes('/api/models')) {
      return Promise.resolve({ data: { models, default: defaults } });
    }
    return Promise.reject(new Error('Unknown URL'));
  });
};

describe('SubjectSelection Component', () => {
  const mockOnSelectionComplete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders subject selection form', async () => {
    setupAPIMocks(['geography', 'science', 'math', 'literature']);

    render(<SubjectSelection onSelectionComplete={mockOnSelectionComplete} />);

    // Wait for categories to load
    await waitFor(() => {
      expect(screen.getByText('🎯 Select Your Quiz Subject')).toBeInTheDocument();
    });

    // Check that the form elements are present
    expect(screen.getByText('Question Source:')).toBeInTheDocument();
    // Initially database source is selected, so should show dropdown
    expect(screen.getByLabelText('Subject:')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Choose a subject...')).toBeInTheDocument();
  });

  test('loads and displays categories', async () => {
    setupAPIMocks(['geography', 'science']);

    render(<SubjectSelection onSelectionComplete={mockOnSelectionComplete} />);

    await waitFor(() => {
      expect(screen.getByText('Geography')).toBeInTheDocument();
      expect(screen.getByText('Science')).toBeInTheDocument();
    });
  });

  test('handles category selection for database questions', async () => {
    setupAPIMocks(['geography']);

    render(<SubjectSelection onSelectionComplete={mockOnSelectionComplete} />);

    await waitFor(() => {
      expect(screen.getByText('Geography')).toBeInTheDocument();
    });

    // Select a category
    const categorySelect = screen.getByLabelText('Subject:');
    fireEvent.change(categorySelect, { target: { value: 'geography' } });

    // Keep database source selected (default)
    const startButton = screen.getByText('Start Quiz');
    fireEvent.click(startButton);

    // Check that callback was called with correct parameters
    expect(mockOnSelectionComplete).toHaveBeenCalledWith({
      category: 'geography',
      source: 'database',
      provider: null,
      model: null
    });
  });

  test('handles custom topic input for AI questions without models', async () => {
    setupAPIMocks(['geography', 'science']);

    render(<SubjectSelection onSelectionComplete={mockOnSelectionComplete} />);

    await waitFor(() => {
      expect(screen.getByText('Geography')).toBeInTheDocument();
    });

    // Select AI questions
    const aiRadio = screen.getByDisplayValue('ai');
    fireEvent.click(aiRadio);

    // Should now show custom topic input instead of dropdown
    expect(screen.getByLabelText('Custom Topic:')).toBeInTheDocument();

    // Enter a custom topic
    const topicInput = screen.getByLabelText('Custom Topic:');
    fireEvent.change(topicInput, { target: { value: 'Ancient Rome' } });

    // Click start quiz
    const startButton = screen.getByText('Start Quiz');
    fireEvent.click(startButton);

    // Check that callback was called with correct parameters
    expect(mockOnSelectionComplete).toHaveBeenCalledWith({
      category: 'Ancient Rome',
      source: 'ai',
      provider: 'ollama',
      model: 'llama3.2'
    });
  });

  test('handles custom topic input for AI questions with models', async () => {
    const models = {
      ollama: [
        { id: 'llama3.2', name: 'Llama 3.2', description: 'Latest model' }
      ]
    };
    const defaults = { ollama: 'llama3.2' };
    setupAPIMocks(['geography'], models, defaults);

    render(<SubjectSelection onSelectionComplete={mockOnSelectionComplete} />);

    await waitFor(() => {
      expect(screen.getByText('Geography')).toBeInTheDocument();
    });

    // Select AI questions
    const aiRadio = screen.getByDisplayValue('ai');
    fireEvent.click(aiRadio);

    // Should show custom topic input and model selection
    expect(screen.getByLabelText('Custom Topic:')).toBeInTheDocument();
    expect(screen.getByText('AI Provider:')).toBeInTheDocument();

    // Enter a custom topic
    const topicInput = screen.getByLabelText('Custom Topic:');
    fireEvent.change(topicInput, { target: { value: 'JavaScript' } });

    // Click start quiz
    const startButton = screen.getByText('Start Quiz');
    fireEvent.click(startButton);

    // Check that callback was called with correct parameters
    expect(mockOnSelectionComplete).toHaveBeenCalledWith({
      category: 'JavaScript',
      source: 'ai',
      provider: 'ollama',
      model: 'llama3.2'
    });
  });

  test('validates required fields', async () => {
    setupAPIMocks(['geography']);

    render(<SubjectSelection onSelectionComplete={mockOnSelectionComplete} />);

    await waitFor(() => {
      expect(screen.getByText('Geography')).toBeInTheDocument();
    });

    // Try to start without selecting category (database mode)
    const startButton = screen.getByText('Start Quiz');
    expect(startButton).toBeDisabled();

    // Switch to AI mode
    const aiRadio = screen.getByDisplayValue('ai');
    fireEvent.click(aiRadio);

    // Try to start without entering topic (AI mode)
    expect(startButton).toBeDisabled();
  });

  test('handles API error gracefully', async () => {
    mockedAxios.get.mockImplementation((url) => {
      if (url.includes('/api/categories')) {
        return Promise.reject(new Error('Network error'));
      }
      if (url.includes('/api/models')) {
        return Promise.resolve({ data: { models: {}, default: {} } });
      }
      return Promise.reject(new Error('Unknown URL'));
    });

    render(<SubjectSelection onSelectionComplete={mockOnSelectionComplete} />);

    await waitFor(() => {
      expect(screen.getByText('Failed to load categories. Please try again later.')).toBeInTheDocument();
    });
  });

  test('default question source is database', async () => {
    setupAPIMocks(['geography']);

    render(<SubjectSelection onSelectionComplete={mockOnSelectionComplete} />);

    await waitFor(() => {
      expect(screen.getByText('Geography')).toBeInTheDocument();
    });

    // Database radio should be selected by default
    const databaseRadio = screen.getByDisplayValue('database');
    expect(databaseRadio).toBeChecked();

    // AI radio should not be selected
    const aiRadio = screen.getByDisplayValue('ai');
    expect(aiRadio).not.toBeChecked();
  });

  test('toggles between dropdown and custom input based on question source', async () => {
    setupAPIMocks(['geography']);

    render(<SubjectSelection onSelectionComplete={mockOnSelectionComplete} />);

    await waitFor(() => {
      expect(screen.getByText('Geography')).toBeInTheDocument();
    });

    // Initially should show dropdown for database questions
    expect(screen.getByLabelText('Subject:')).toBeInTheDocument();
    expect(screen.queryByLabelText('Custom Topic:')).not.toBeInTheDocument();

    // Switch to AI questions
    const aiRadio = screen.getByDisplayValue('ai');
    fireEvent.click(aiRadio);

    // Should now show custom topic input
    expect(screen.queryByLabelText('Subject:')).not.toBeInTheDocument();
    expect(screen.getByLabelText('Custom Topic:')).toBeInTheDocument();

    // Switch back to database questions
    const databaseRadio = screen.getByDisplayValue('database');
    fireEvent.click(databaseRadio);

    // Should show dropdown again
    expect(screen.getByLabelText('Subject:')).toBeInTheDocument();
    expect(screen.queryByLabelText('Custom Topic:')).not.toBeInTheDocument();
  });
});