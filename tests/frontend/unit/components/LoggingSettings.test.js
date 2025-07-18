import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import LoggingSettings from '../../../../frontend/src/components/LoggingSettings';

// Mock axios
jest.mock('axios', () => ({
  get: jest.fn(),
  put: jest.fn(),
  post: jest.fn()
}));

const axios = require('axios');

describe('LoggingSettings', () => {
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
  });

  test('renders logging configuration interface', async () => {
    // Mock API responses
    axios.get.mockImplementation((url) => {
      if (url.includes('/api/logging/config')) {
        return Promise.resolve({
          data: {
            config: {
              log_levels: {
                frontend: { app: 'INFO' },
                backend: { api: 'INFO', llm: 'INFO', database: 'INFO' }
              },
              file_settings: {
                enable_file_logging: true,
                log_directory: 'logs',
                max_file_size_mb: 10,
                max_backup_files: 5,
                log_format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
              },
              monitoring: {
                enable_live_viewer: true,
                max_recent_entries: 100,
                auto_refresh_interval: 5000
              }
            },
            available_levels: ['ERROR', 'WARN', 'INFO', 'DEBUG', 'TRACE']
          }
        });
      } else if (url.includes('/api/logging/files')) {
        return Promise.resolve({
          data: {
            files: [
              {
                path: 'backend/api.log',
                full_path: 'logs/backend/api.log',
                size: 1024,
                modified: '2023-01-01T00:00:00Z',
                component: 'backend/api'
              }
            ]
          }
        });
      } else if (url.includes('/api/logging/recent')) {
        return Promise.resolve({
          data: {
            logs: [
              {
                timestamp: '2023-01-01T00:00:00Z',
                component: 'backend/api',
                message: 'Test log message',
                level: 'INFO'
              }
            ]
          }
        });
      } else if (url.includes('/api/logging/llm-prompts')) {
        return Promise.resolve({
          data: {
            logs: []
          }
        });
      }
      return Promise.reject(new Error('Unknown URL'));
    });

    render(<LoggingSettings />);

    // Wait for the component to load
    await waitFor(() => {
      expect(screen.getByText('🔧 Logging Configuration')).toBeInTheDocument();
    });

    // Check if tabs are rendered
    expect(screen.getByText('📊 Log Levels')).toBeInTheDocument();
    expect(screen.getByText('📁 Log Files')).toBeInTheDocument();
    expect(screen.getByText('👁️ Live Monitor')).toBeInTheDocument();

    // Check if log level controls are rendered
    expect(screen.getByText('Frontend Components')).toBeInTheDocument();
    expect(screen.getByText('Backend Components')).toBeInTheDocument();
  });

  test('renders LLM prompt logging configuration', async () => {
    // Mock API responses with LLM prompt logging
    axios.get.mockImplementation((url) => {
      if (url.includes('/api/logging/config')) {
        return Promise.resolve({
          data: {
            config: {
              log_levels: {
                frontend: { app: 'INFO' },
                backend: { api: 'INFO', llm: 'INFO', database: 'INFO' }
              },
              llm_prompt_logging: {
                enabled: true,
                level: 'DEBUG',
                log_file: 'llm_prompts.log',
                include_metadata: true,
                include_timing: true,
                include_full_response: false
              }
            },
            available_levels: ['ERROR', 'WARN', 'INFO', 'DEBUG', 'TRACE']
          }
        });
      } else if (url.includes('/api/logging/files')) {
        return Promise.resolve({
          data: {
            files: []
          }
        });
      } else if (url.includes('/api/logging/recent')) {
        return Promise.resolve({
          data: {
            logs: []
          }
        });
      } else if (url.includes('/api/logging/llm-prompts')) {
        return Promise.resolve({
          data: {
            logs: [{
              timestamp: '2025-01-01T12:00:00Z',
              provider: 'test_provider',
              model: 'test_model',
              level: 'INFO',
              status: 'success',
              prompt_preview: 'Test prompt',
              metadata: { subject: 'test' },
              timing: { duration_ms: 100 }
            }]
          }
        });
      }
      return Promise.reject(new Error('Unknown URL'));
    });

    render(<LoggingSettings />);

    // Wait for configuration to load
    await waitFor(() => {
      expect(screen.getByText('🔧 Logging Configuration')).toBeInTheDocument();
    });

    // Check if LLM prompt logging section is rendered
    expect(screen.getByText('🤖 LLM Prompt Logging')).toBeInTheDocument();
    expect(screen.getByText('Enable LLM Prompt Logging')).toBeInTheDocument();
    
    // Wait for the configuration to be loaded and checkbox to be checked
    await waitFor(() => {
      const enableToggle = screen.getByRole('checkbox', { name: /Enable LLM Prompt Logging/ });
      expect(enableToggle).toBeChecked();
    });
    
    // Wait for logging level dropdown to be visible and have correct value
    await waitFor(() => {
      const select = screen.getByRole('combobox');
      expect(select).toBeInTheDocument();
      expect(select.value).toBe('DEBUG');
    });
  });

  test('switches between tabs correctly', async () => {
    // Mock API responses for all tabs
    axios.get.mockImplementation((url) => {
      if (url.includes('/api/logging/config')) {
        return Promise.resolve({
          data: {
            config: {
              log_levels: {
                frontend: { app: 'INFO' },
                backend: { api: 'INFO', llm: 'INFO', database: 'INFO' }
              }
            },
            available_levels: ['ERROR', 'WARN', 'INFO', 'DEBUG', 'TRACE']
          }
        });
      } else if (url.includes('/api/logging/files')) {
        return Promise.resolve({
          data: {
            files: []
          }
        });
      } else if (url.includes('/api/logging/recent')) {
        return Promise.resolve({
          data: {
            logs: []
          }
        });
      } else if (url.includes('/api/logging/llm-prompts')) {
        return Promise.resolve({
          data: {
            logs: []
          }
        });
      }
      return Promise.reject(new Error('Unknown URL'));
    });

    render(<LoggingSettings />);

    await waitFor(() => {
      expect(screen.getByText('🔧 Logging Configuration')).toBeInTheDocument();
    });

    // Click on Log Files tab
    const logFilesTab = screen.getByText('📁 Log Files');
    fireEvent.click(logFilesTab);

    await waitFor(() => {
      expect(screen.getByText('Log File Management')).toBeInTheDocument();
    });

    // Click on Live Monitor tab
    const liveMonitorTab = screen.getByText('👁️ Live Monitor');
    fireEvent.click(liveMonitorTab);

    await waitFor(() => {
      expect(screen.getByText('Live Log Monitor')).toBeInTheDocument();
    });
  });

  test('saves configuration changes', async () => {
    // Mock API responses
    axios.get.mockImplementation((url) => {
      if (url.includes('/api/logging/config')) {
        return Promise.resolve({
          data: {
            config: {
              log_levels: {
                frontend: { app: 'INFO' },
                backend: { api: 'INFO', llm: 'INFO', database: 'INFO' }
              }
            },
            available_levels: ['ERROR', 'WARN', 'INFO', 'DEBUG', 'TRACE']
          }
        });
      } else if (url.includes('/api/logging/files')) {
        return Promise.resolve({
          data: {
            files: []
          }
        });
      } else if (url.includes('/api/logging/recent')) {
        return Promise.resolve({
          data: {
            logs: []
          }
        });
      } else if (url.includes('/api/logging/llm-prompts')) {
        return Promise.resolve({
          data: {
            logs: []
          }
        });
      }
      return Promise.reject(new Error('Unknown URL'));
    });

    axios.put.mockResolvedValue({
      data: {
        success: true,
        config: {
          log_levels: {
            frontend: { app: 'INFO' },
            backend: { api: 'DEBUG', llm: 'INFO', database: 'INFO' }
          }
        }
      }
    });

    render(<LoggingSettings />);

    await waitFor(() => {
      expect(screen.getByText('Save Configuration')).toBeInTheDocument();
    });

    // Click save button
    const saveButton = screen.getByText('Save Configuration');
    fireEvent.click(saveButton);

    // Wait for success message
    await waitFor(() => {
      expect(screen.getByText('Logging configuration saved successfully!')).toBeInTheDocument();
    });
  });
});