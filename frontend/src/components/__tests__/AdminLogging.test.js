import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AdminLogging from '../AdminLogging';

// Mock a basic fetch since the component uses it extensively
global.fetch = jest.fn();

const mockConfigData = {
  global_level: "INFO",
  frontend_level: "INFO",
  backend_levels: {
    api_server: "INFO",
    llm_providers: "INFO",
    database: "WARNING"
  },
  log_files: {
    frontend_app: "logs/frontend/app.log",
    backend_api: "logs/backend/api.log",
    backend_llm: "logs/backend/llm.log",
    backend_database: "logs/backend/database.log",
    backend_error: "logs/backend/error.log",
    combined: "logs/combined.log"
  },
  log_rotation_max_bytes: 10485760,
  log_rotation_backup_count: 5,
  enable_file_logging: true
};

const mockLogEntriesData = {
    logs: [
        "2023-10-26 ... INFO - Log entry 1",
        "2023-10-26 ... DEBUG - Log entry 2",
        "2023-10-26 ... WARNING - Log entry 3",
    ],
    file: "logs/combined.log",
    count: 3
};

describe('AdminLogging Component', () => {
  beforeEach(() => {
    // Reset mocks before each test
    fetch.mockClear();
    // Default successful fetch for config
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockConfigData),
      })
    );
  });

  test('renders loading state initially', () => {
    render(<AdminLogging />);
    expect(screen.getByText(/Loading logging configuration.../i)).toBeInTheDocument();
  });

  test('fetches and displays logging configuration', async () => {
    render(<AdminLogging />);
    await waitFor(() => {
      expect(screen.getByLabelText(/Backend Global Level:/i)).toHaveValue('INFO');
    });
    expect(screen.getByLabelText(/API Server:/i)).toHaveValue('INFO');
    expect(screen.getByText(/Max Log File Size: 10.00 MB/i)).toBeInTheDocument(); // Example from mockConfigData
  });

  test('allows changing a log level and attempts to save', async () => {
    fetch.mockImplementationOnce(() => // For initial load
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockConfigData),
      })
    );
    // Mock for the PUT request
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ message: 'Log levels updated successfully!', config: { ...mockConfigData, global_level: 'DEBUG' } }),
      })
    );

    render(<AdminLogging />);
    await waitFor(() => screen.getByLabelText(/Backend Global Level:/i)); // Ensure loaded

    const globalLevelSelect = screen.getByLabelText(/Backend Global Level:/i);
    fireEvent.change(globalLevelSelect, { target: { value: 'DEBUG' } });
    expect(globalLevelSelect).toHaveValue('DEBUG');

    const saveButton = screen.getByRole('button', { name: /Save Log Levels/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/logging/config'),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify(expect.objectContaining({ global_level: 'DEBUG' })),
        })
      );
      expect(screen.getByText(/Log levels updated successfully!/i)).toBeInTheDocument();
    });
  });

  test('displays log files and action buttons', async () => {
    render(<AdminLogging />);
    await waitFor(() => screen.getByText('backend/api.log')); // Wait for table to populate

    expect(screen.getByText('backend_api')).toBeInTheDocument();
    expect(screen.getByText('logs/backend/api.log')).toBeInTheDocument();

    const downloadButtons = screen.getAllByRole('button', { name: /Download/i });
    expect(downloadButtons.length).toBeGreaterThan(0);
    // Example: check for a specific log file's download button
    const backendApiRow = screen.getByText('backend_api').closest('tr');
    expect(within(backendApiRow).getByRole('button', {name: /Download/i})).toBeInTheDocument();
    expect(within(backendApiRow).getByRole('button', {name: /Clear/i})).toBeInTheDocument();
    expect(within(backendApiRow).getByRole('button', {name: /Rotate/i})).toBeInTheDocument();
  });

  test('fetches and displays log entries when a log file is selected', async () => {
    // First fetch for config
    fetch.mockImplementationOnce(() => Promise.resolve({ ok: true, json: () => Promise.resolve(mockConfigData) }));
    // Second fetch for logs
    fetch.mockImplementationOnce(() => Promise.resolve({ ok: true, json: () => Promise.resolve(mockLogEntriesData) }));

    render(<AdminLogging />);
    await waitFor(() => screen.getByLabelText(/View Log:/i)); // Config loaded

    const logFileSelect = screen.getByLabelText(/View Log:/i);
    // The options are populated based on mockConfigData.log_files keys
    // Example: select "combined" log
    fireEvent.change(logFileSelect, { target: { value: 'combined' } });

    await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
            expect.stringContaining('/api/logging/logs?component=combined&lines=100'),
            undefined // For GET request
        );
        expect(screen.getByText(/Log entry 1/i)).toBeInTheDocument();
        expect(screen.getByText(/Log entry 2/i)).toBeInTheDocument();
    });
  });

  test('handles error when fetching configuration fails', async () => {
    fetch.mockReset(); // Clear default mock
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ detail: 'Server Error' }),
      })
    );
    render(<AdminLogging />);
    await waitFor(() => {
      expect(screen.getByText(/Error: Failed to fetch logging configuration: Server Error/i)).toBeInTheDocument();
    });
  });

});

// Helper to use RTL queries within a specific element scope
const within = (element) => ({
    getByText: (text, options) => screen.getByText(text, { container: element, ...options }),
    getByRole: (role, options) => screen.getByRole(role, { container: element, ...options }),
    // Add other queries as needed
});
