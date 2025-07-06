import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import SubjectSelection from '@components/SubjectSelection';

// Mock axios
jest.mock('axios', () => ({
  get: jest.fn()
}));

import axios from 'axios';
const mockedAxios = axios;

const setupMocks = (categories = []) => {
  mockedAxios.get.mockImplementation((url) => {
    if (url.includes('/api/categories')) {
      return Promise.resolve({ data: { categories } });
    }
    return Promise.resolve({ data: {} });
  });
};

describe('SubjectSelection Component', () => {
  const mockOnSelectionComplete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders subject selection form', async () => {
    setupMocks(['geography', 'science', 'math', 'literature']);

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
    setupMocks(['geography', 'science']);

    render(<SubjectSelection onSelectionComplete={mockOnSelectionComplete} />);

    await waitFor(() => {
      expect(screen.getByText('Geography')).toBeInTheDocument();
      expect(screen.getByText('Science')).toBeInTheDocument();
    });
  });

  test('handles category selection and question source selection', async () => {
    setupMocks(['geography', 'science']);

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
      source: 'database'
    });
  });

  test('handles custom topic input for AI questions', async () => {
    setupMocks(['geography', 'science']);

    render(<SubjectSelection onSelectionComplete={mockOnSelectionComplete} />);

    await waitFor(() => {
      expect(screen.getByText('Geography')).toBeInTheDocument();
    });

    // Select AI questions
    const aiRadio = screen.getByDisplayValue('ai');
    fireEvent.click(aiRadio);

    // Should now show custom topic input instead of dropdown
    expect(screen.getByLabelText('Custom Topic:')).toBeInTheDocument();
    expect(screen.queryByLabelText('Subject:')).not.toBeInTheDocument();

    // Enter custom topic
    const customTopicInput = screen.getByLabelText('Custom Topic:');
    fireEvent.change(customTopicInput, { target: { value: 'Ancient Rome' } });

    // Click start quiz button
    const startButton = screen.getByText('Start Quiz');
    fireEvent.click(startButton);

    // Check that callback was called with correct parameters (no model anymore)
    expect(mockOnSelectionComplete).toHaveBeenCalledWith({
      category: 'Ancient Rome',
      source: 'ai'
    });
  });

  test('shows no model dropdown for AI questions since model is now managed in admin panel', async () => {
    setupMocks(['geography']);

    render(<SubjectSelection onSelectionComplete={mockOnSelectionComplete} />);

    await waitFor(() => {
      expect(screen.getByText('Geography')).toBeInTheDocument();
    });

    const aiRadio = screen.getByDisplayValue('ai');
    fireEvent.click(aiRadio);

    // Model dropdown should no longer be present since it's managed in admin panel
    expect(screen.queryByLabelText('Model:')).not.toBeInTheDocument();
    // Should only show custom topic input
    expect(screen.getByLabelText('Custom Topic:')).toBeInTheDocument();
  });

  test('shows error when no subject is selected', async () => {
    setupMocks(['geography']);

    render(<SubjectSelection onSelectionComplete={mockOnSelectionComplete} />);

    await waitFor(() => {
      expect(screen.getByText('Geography')).toBeInTheDocument();
    });

    // The button should be disabled initially for database questions
    const startButton = screen.getByText('Start Quiz');
    expect(startButton).toBeDisabled();

    // Since the component prevents clicking when no category is selected,
    // we need to test the error state differently - by checking button state
    expect(mockOnSelectionComplete).not.toHaveBeenCalled();
  });

  test('shows error when no custom topic is entered for AI questions', async () => {
    setupMocks(['geography']);

    render(<SubjectSelection onSelectionComplete={mockOnSelectionComplete} />);

    await waitFor(() => {
      expect(screen.getByText('Geography')).toBeInTheDocument();
    });

    // Select AI questions
    const aiRadio = screen.getByDisplayValue('ai');
    fireEvent.click(aiRadio);

    // Button should be disabled when no custom topic is entered
    const startButton = screen.getByText('Start Quiz');
    expect(startButton).toBeDisabled();

    expect(mockOnSelectionComplete).not.toHaveBeenCalled();
  });

  test('handles API error gracefully', async () => {
    mockedAxios.get.mockImplementation(() => Promise.reject(new Error('Network error')));

    render(<SubjectSelection onSelectionComplete={mockOnSelectionComplete} />);

    await waitFor(() => {
      expect(screen.getByText('Failed to load categories. Please try again later.')).toBeInTheDocument();
    });

    // Should show retry button
    expect(screen.getByText('Try Again')).toBeInTheDocument();
  });

  test('default question source is database', async () => {
    setupMocks(['geography']);

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
    setupMocks(['geography']);

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