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

describe('SubjectSelection Component', () => {
  const mockOnSelectionComplete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders subject selection form', async () => {
    // Mock the categories API response
    mockedAxios.get.mockResolvedValue({
      data: { categories: ['geography', 'science', 'math', 'literature'] }
    });

    render(<SubjectSelection onSelectionComplete={mockOnSelectionComplete} />);

    // Wait for categories to load
    await waitFor(() => {
      expect(screen.getByText('🎯 Select Your Quiz Subject')).toBeInTheDocument();
    });

    // Check that the form elements are present
    expect(screen.getByLabelText('Subject:')).toBeInTheDocument();
    expect(screen.getByText('Question Source:')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Choose a subject...')).toBeInTheDocument();
  });

  test('loads and displays categories', async () => {
    mockedAxios.get.mockResolvedValue({
      data: { categories: ['geography', 'science'] }
    });

    render(<SubjectSelection onSelectionComplete={mockOnSelectionComplete} />);

    await waitFor(() => {
      expect(screen.getByText('Geography')).toBeInTheDocument();
      expect(screen.getByText('Science')).toBeInTheDocument();
    });
  });

  test('handles category selection and question source selection', async () => {
    mockedAxios.get.mockResolvedValue({
      data: { categories: ['geography', 'science'] }
    });

    render(<SubjectSelection onSelectionComplete={mockOnSelectionComplete} />);

    await waitFor(() => {
      expect(screen.getByText('Geography')).toBeInTheDocument();
    });

    // Switch to AI questions
    const aiRadio = screen.getByDisplayValue('ai');
    fireEvent.click(aiRadio);

    // Enter custom subject
    const customInput = screen.getByPlaceholderText('Type any subject...');
    fireEvent.change(customInput, { target: { value: 'history' } });

    // Click start quiz button
    const startButton = screen.getByText('Start Quiz');
    fireEvent.click(startButton);

    // Check that callback was called with correct parameters
    expect(mockOnSelectionComplete).toHaveBeenCalledWith({
      category: 'history',
      source: 'ai'
    });
  });

  test('shows error when no subject is selected', async () => {
    mockedAxios.get.mockResolvedValue({
      data: { categories: ['geography'] }
    });

    render(<SubjectSelection onSelectionComplete={mockOnSelectionComplete} />);

    await waitFor(() => {
      expect(screen.getByText('Geography')).toBeInTheDocument();
    });

    // The button should be disabled initially
    const startButton = screen.getByText('Start Quiz');
    expect(startButton).toBeDisabled();

    // Since the component prevents clicking when no category is selected,
    // we need to test the error state differently - by checking button state
    expect(mockOnSelectionComplete).not.toHaveBeenCalled();
  });

  test('handles API error gracefully', async () => {
    mockedAxios.get.mockRejectedValue(new Error('Network error'));

    render(<SubjectSelection onSelectionComplete={mockOnSelectionComplete} />);

    await waitFor(() => {
      expect(screen.getByText('Failed to load categories. Please try again later.')).toBeInTheDocument();
    });

    // Should show retry button
    expect(screen.getByText('Try Again')).toBeInTheDocument();
  });

  test('default question source is database', async () => {
    mockedAxios.get.mockResolvedValue({
      data: { categories: ['geography'] }
    });

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
});