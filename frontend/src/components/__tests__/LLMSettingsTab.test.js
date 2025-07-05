import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import LLMSettingsTab from '../LLMSettingsTab';

// Mock axios
jest.mock('axios');

const mockLlmProvidersResponse = {
  current_provider: 'ollama',
  current_model: 'llama3.2',
  available_providers: [
    { name: 'ollama', healthy: true, models: ['llama3.2', 'codellama'] },
    { name: 'openai', healthy: true, models: ['gpt-4o-mini', 'gpt-4'] },
  ],
};

const mockModelsResponseOllama = {
  provider: 'ollama',
  models: ['llama3.2', 'codellama', 'test-ollama-model'],
};

const mockModelsResponseOpenAI = {
  provider: 'openai',
  models: ['gpt-4o-mini', 'gpt-4', 'gpt-3.5-turbo'],
};

const mockHealthResponseHealthy = {
  provider: 'ollama',
  healthy: true,
  models: ['llama3.2', 'codellama'],
  message: 'Healthy',
};

const mockHealthResponseUnhealthy = {
  provider: 'openai',
  healthy: false,
  error: 'Service unavailable',
  models: [],
  message: 'Service unavailable',
};


describe('LLMSettingsTab', () => {
  beforeEach(() => {
    axios.get.mockImplementation((url) => {
      if (url.includes('/api/llm/providers')) {
        return Promise.resolve({ data: mockLlmProvidersResponse });
      }
      if (url.includes('/api/models?provider=ollama')) {
        return Promise.resolve({ data: mockModelsResponseOllama });
      }
      if (url.includes('/api/models?provider=openai')) {
        return Promise.resolve({ data: mockModelsResponseOpenAI });
      }
      if (url.includes('/api/llm/health?provider_name=ollama')) {
        return Promise.resolve({ data: mockHealthResponseHealthy });
      }
      if (url.includes('/api/llm/health?provider_name=openai')) {
        // Simulate initial load for openai as unhealthy for variety
        return Promise.resolve({ data: mockHealthResponseUnhealthy });
      }
      return Promise.reject(new Error('not found'));
    });
    axios.post.mockResolvedValue({ data: {} });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state initially', () => {
    axios.get.mockImplementationOnce(() => new Promise(() => {})); // Keep it pending
    render(<LLMSettingsTab onConfigUpdate={jest.fn()} />);
    expect(screen.getByText(/Loading LLM Settings.../i)).toBeInTheDocument();
  });

  test('fetches and displays initial LLM configuration', async () => {
    render(<LLMSettingsTab onConfigUpdate={jest.fn()} />);

    await waitFor(() => {
      expect(screen.getByText(/Currently Active:/i)).toBeInTheDocument();
      expect(screen.getByText(/ollama/i)).toBeInTheDocument();
      expect(screen.getByText(/llama3.2/i)).toBeInTheDocument();
    });

    // Check provider dropdown
    const providerSelect = screen.getByLabelText(/LLM Provider:/i);
    expect(providerSelect).toHaveValue('ollama');
    expect(screen.getByRole('option', { name: /Ollama \(Healthy\)/i })).toBeInTheDocument();
    // OpenAI initially unhealthy in this mock setup
    expect(screen.getByRole('option', { name: /Openai \(Unhealthy\)/i })).toBeInTheDocument();


    // Check model dropdown
    const modelSelect = screen.getByLabelText(/Model:/i);
    await waitFor(() => {
        // Models for 'ollama' (current_provider) should be populated from mockLlmProvidersResponse
        expect(modelSelect).toHaveValue('llama3.2');
        expect(screen.getByRole('option', { name: 'llama3.2' })).toBeInTheDocument();
        expect(screen.getByRole('option', { name: 'codellama' })).toBeInTheDocument();
    });
  });

  test('fetches and displays models when provider is changed', async () => {
    render(<LLMSettingsTab onConfigUpdate={jest.fn()} />);

    await waitFor(() => {
      expect(screen.getByLabelText(/LLM Provider:/i)).toBeInTheDocument();
    });

    const providerSelect = screen.getByLabelText(/LLM Provider:/i);
    fireEvent.change(providerSelect, { target: { value: 'openai' } });

    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith(expect.stringContaining('/api/models?provider=openai'));
    });

    const modelSelect = screen.getByLabelText(/Model:/i);
    await waitFor(() => {
        expect(modelSelect.value).toBe('gpt-4o-mini'); // First model from mockModelsResponseOpenAI
        expect(screen.getByRole('option', { name: 'gpt-4o-mini' })).toBeInTheDocument();
        expect(screen.getByRole('option', { name: 'gpt-4' })).toBeInTheDocument();
    });
  });

  test('saves configuration when save button is clicked', async () => {
    const mockOnConfigUpdate = jest.fn();
    axios.get.mockResolvedValue({ data: mockLlmProvidersResponse }); // Ensure initial load is fine
    axios.post.mockResolvedValue({ data: { provider: 'openai', model: 'gpt-4' } });


    render(<LLMSettingsTab onConfigUpdate={mockOnConfigUpdate} />);

    await waitFor(() => screen.getByLabelText(/LLM Provider:/i));

    fireEvent.change(screen.getByLabelText(/LLM Provider:/i), { target: { value: 'openai' } });

    await waitFor(() => screen.getByLabelText(/Model:/i));
    // Wait for models of 'openai' to load
    await waitFor(() => expect(screen.getByRole('option', {name: 'gpt-4o-mini'})).toBeInTheDocument());

    fireEvent.change(screen.getByLabelText(/Model:/i), { target: { value: 'gpt-4' } });

    fireEvent.click(screen.getByRole('button', { name: /Save Configuration/i }));

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/api/llm/config'),
        { provider: 'openai', model: 'gpt-4' }
      );
    });

    expect(screen.getByText(/Configuration saved successfully!/i)).toBeInTheDocument();
    expect(mockOnConfigUpdate).toHaveBeenCalled();

    // Check if current display updated
     await waitFor(() => {
      expect(screen.getByText((content, element) => {
        return element.tagName.toLowerCase() === 'span' && element.classList.contains('provider-value') && content === 'openai';
      })).toBeInTheDocument();
      expect(screen.getByText((content, element) => {
        return element.tagName.toLowerCase() === 'span' && element.classList.contains('model-value') && content === 'gpt-4';
      })).toBeInTheDocument();
    });
  });

  test('handles save error from API', async () => {
    axios.post.mockRejectedValue({
        response: { data: { detail: 'Failed to save from API' } }
    });
    render(<LLMSettingsTab onConfigUpdate={jest.fn()} />);

    await waitFor(() => screen.getByLabelText(/LLM Provider:/i));
    fireEvent.change(screen.getByLabelText(/LLM Provider:/i), { target: { value: 'ollama' } });

    await waitFor(() => screen.getByLabelText(/Model:/i));
    await waitFor(() => expect(screen.getByRole('option', {name: 'llama3.2'})).toBeInTheDocument());
    fireEvent.change(screen.getByLabelText(/Model:/i), { target: { value: 'codellama' } });

    fireEvent.click(screen.getByRole('button', { name: /Save Configuration/i }));

    await waitFor(() => {
      expect(screen.getByText(/Failed to save from API/i)).toBeInTheDocument();
    });
  });

  test('refreshes health check when button is clicked', async () => {
    // Initial setup with Ollama as healthy
    axios.get.mockImplementation((url) => {
      if (url.includes('/api/llm/providers')) return Promise.resolve({ data: mockLlmProvidersResponse });
      if (url.includes('/api/llm/health?provider_name=ollama')) return Promise.resolve({ data: mockHealthResponseHealthy });
      if (url.includes('/api/models?provider=ollama')) return Promise.resolve({ data: mockModelsResponseOllama });
      return Promise.reject(new Error('not found'));
    });

    render(<LLMSettingsTab onConfigUpdate={jest.fn()} />);

    await waitFor(() => {
      expect(screen.getByRole('option', { name: /Ollama \(Healthy\)/i })).toBeInTheDocument();
    });

    // Change health response for ollama to unhealthy for the refresh call
    axios.get.mockImplementation((url) => {
        if (url.includes('/api/llm/providers')) return Promise.resolve({ data: mockLlmProvidersResponse });
        if (url.includes('/api/llm/health?provider_name=ollama')) {
            // This is the refreshed call
            return Promise.resolve({data: {...mockHealthResponseUnhealthy, provider: 'ollama'}});
        }
        if (url.includes('/api/models?provider=ollama')) return Promise.resolve({ data: mockModelsResponseOllama });
        return Promise.reject(new Error('not found'));
    });

    const refreshButton = screen.getByRole('button', { name: /Refresh Health/i });
    fireEvent.click(refreshButton);

    expect(screen.getByText(/Checking.../i)).toBeInTheDocument(); // Intermediate state

    await waitFor(() => {
      // Now expect Ollama to show as unhealthy
      expect(screen.getByRole('option', { name: /Ollama \(Unhealthy\)/i })).toBeInTheDocument();
      expect(screen.getByText(mockHealthResponseUnhealthy.message)).toBeInTheDocument();
    });
     // Ensure the correct number of calls to health endpoint
     // Initial loads (ollama, openai) + 1 manual refresh for ollama
    expect(axios.get).toHaveBeenCalledWith(expect.stringContaining('/api/llm/health?provider_name=ollama'));
    // The count depends on how many providers are iterated for initial health checks.
    // In the current setup, it's called for each provider in availableProviders during fetchInitialConfig.
    // And then once more for the selectedProvider if its health wasn't fetched.
    // Plus the manual click.
    // So, for 'ollama': once on load, once on refresh.
    // For 'openai': once on load.
    // Let's verify specific calls were made.
    expect(axios.get).toHaveBeenCalledWith(expect.stringContaining('/api/llm/health?provider_name=openai'));
  });

});
