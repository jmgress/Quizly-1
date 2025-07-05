import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import App from '../App'; // Assuming App.js is in src folder

// Mock child components
jest.mock('../components/Quiz', () => () => <div data-testid="quiz-component">Quiz Component</div>);
jest.mock('../components/SubjectSelection', () => ({onSelectionComplete}) => (
    <div data-testid="subject-selection-component">
        Subject Selection Component
        <button onClick={() => onSelectionComplete({ category: 'TestCategory', source: 'database' })}>
            Complete Selection
        </button>
    </div>
));
jest.mock('../components/AdminPanel', () => ({onGoHome, onConfigUpdate}) => (
    <div data-testid="admin-panel-component">
        Admin Panel Component
        <button onClick={onGoHome}>Go Home from Admin</button>
        <button onClick={onConfigUpdate}>Update Config from Admin</button>
    </div>
));

// Mock axios for LLM config fetching
jest.mock('axios');

const mockLlmConfigResponse = {
  provider: 'ollama',
  model: 'llama3.2',
};

describe('App Component', () => {
  beforeEach(() => {
    // Setup default axios mock for LLM config
    axios.get.mockImplementation((url) => {
      if (url.includes('/api/llm/config')) {
        return Promise.resolve({ data: mockLlmConfigResponse });
      }
      return Promise.reject(new Error(`Unhandled GET request: ${url}`));
    });
    // Reset window.location.hash
    window.location.hash = '';
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders home screen by default and displays LLM config info', async () => {
    render(<App />);
    expect(screen.getByText(/Quizly/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Start Quiz/i })).toBeInTheDocument();

    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith(expect.stringContaining('/api/llm/config'));
      expect(screen.getByText(/AI Questions powered by ollama \(llama3.2\)/i)).toBeInTheDocument();
    });
  });

  test('navigates to subject selection on "Start Quiz" click', async () => {
    render(<App />);
    await waitFor(() => expect(screen.getByText(/AI Questions powered by/i)).toBeInTheDocument()); // Ensure initial load is done

    fireEvent.click(screen.getByRole('button', { name: /Start Quiz/i }));
    expect(screen.getByTestId('subject-selection-component')).toBeInTheDocument();
  });

  test('navigates to quiz screen after subject selection', async () => {
    render(<App />);
    await waitFor(() => expect(screen.getByText(/AI Questions powered by/i)).toBeInTheDocument());

    fireEvent.click(screen.getByRole('button', { name: /Start Quiz/i }));
    expect(screen.getByTestId('subject-selection-component')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /Complete Selection/i }));
    expect(screen.getByTestId('quiz-component')).toBeInTheDocument();
  });

  test('navigates to admin panel on "Admin Panel" button click', async () => {
    render(<App />);
    await waitFor(() => expect(screen.getByText(/AI Questions powered by/i)).toBeInTheDocument());

    fireEvent.click(screen.getByRole('button', { name: /Admin Panel/i }));
    expect(screen.getByTestId('admin-panel-component')).toBeInTheDocument();
    expect(window.location.hash).toBe('#admin');
  });

  test('navigates to admin panel if hash is #admin on load', async () => {
    window.location.hash = '#admin';
    render(<App />);
    await waitFor(() => { // Wait for async effects in App.js (fetchLlmConfig, checkHash)
        expect(screen.getByTestId('admin-panel-component')).toBeInTheDocument();
    });
  });

  test('navigates home from admin panel', async () => {
    window.location.hash = '#admin';
    render(<App />);
    await waitFor(() => expect(screen.getByTestId('admin-panel-component')).toBeInTheDocument());

    fireEvent.click(screen.getByText('Go Home from Admin')); // Button from AdminPanel mock

    await waitFor(() => expect(screen.getByText(/Quizly/i)).toBeInTheDocument());
    expect(window.location.hash).toBe('');
  });

  test('fetches LLM config again when onConfigUpdate is called from AdminPanel', async () => {
    render(<App />);
    await waitFor(() => expect(axios.get).toHaveBeenCalledTimes(1)); // Initial fetch

    fireEvent.click(screen.getByRole('button', { name: /Admin Panel/i }));
    await waitFor(() => expect(screen.getByTestId('admin-panel-component')).toBeInTheDocument());

    // Simulate config update from AdminPanel mock
    axios.get.mockResolvedValueOnce({ data: { provider: 'openai', model: 'gpt-4-test' } });
    fireEvent.click(screen.getByText('Update Config from Admin'));

    await waitFor(() => expect(axios.get).toHaveBeenCalledTimes(2)); // Initial + update
    expect(axios.get).toHaveBeenLastCalledWith(expect.stringContaining('/api/llm/config'));

    // Check if the display on home screen would update (if we were to navigate back)
    // This part is tricky because App state updates but we are still "on" admin screen in this test setup
    // For simplicity, we've verified fetchLlmConfig was called.
    // To verify UI update, we'd need to navigate home and check the text.

    // Let's navigate home to see the updated text
    fireEvent.click(screen.getByText('Go Home from Admin'));
     await waitFor(() => {
      expect(screen.getByText(/AI Questions powered by openai \(gpt-4-test\)/i)).toBeInTheDocument();
    });
  });

});
