import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import LogLevelSlider from '../../../../frontend/src/components/LogLevelSlider';

describe('LogLevelSlider', () => {
  test('renders slider with correct initial value', () => {
    const mockOnChange = jest.fn();
    render(
      <LogLevelSlider
        label="Test Component:"
        value="INFO"
        onChange={mockOnChange}
      />
    );

    expect(screen.getByLabelText(/Test Component: log level/)).toBeInTheDocument();
    expect(screen.getByDisplayValue('2')).toBeInTheDocument(); // INFO is position 2
    expect(screen.getByText('INFO')).toHaveClass('active');
  });

  test('calls onChange when slider value changes', () => {
    const mockOnChange = jest.fn();
    render(
      <LogLevelSlider
        label="Test Component:"
        value="INFO"
        onChange={mockOnChange}
      />
    );

    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: '3' } });

    expect(mockOnChange).toHaveBeenCalledWith('DEBUG');
  });

  test('displays correct log levels', () => {
    const mockOnChange = jest.fn();
    render(
      <LogLevelSlider
        label="Test Component:"
        value="WARN"
        onChange={mockOnChange}
      />
    );

    expect(screen.getByText('ERROR')).toBeInTheDocument();
    expect(screen.getByText('WARN')).toBeInTheDocument();
    expect(screen.getByText('INFO')).toBeInTheDocument();
    expect(screen.getByText('DEBUG')).toBeInTheDocument();
    expect(screen.getByText('TRACE')).toBeInTheDocument();
    
    expect(screen.getByText('WARN')).toHaveClass('active');
  });

  test('handles keyboard navigation', () => {
    const mockOnChange = jest.fn();
    render(
      <LogLevelSlider
        label="Test Component:"
        value="INFO"
        onChange={mockOnChange}
      />
    );

    const slider = screen.getByRole('slider');
    
    // Test arrow right (increase verbosity)
    fireEvent.keyDown(slider, { key: 'ArrowRight' });
    expect(mockOnChange).toHaveBeenCalledWith('DEBUG');

    // Test arrow left (decrease verbosity)
    fireEvent.keyDown(slider, { key: 'ArrowLeft' });
    expect(mockOnChange).toHaveBeenCalledWith('WARN');
  });

  test('handles disabled state', () => {
    const mockOnChange = jest.fn();
    render(
      <LogLevelSlider
        label="Test Component:"
        value="INFO"
        onChange={mockOnChange}
        disabled={true}
      />
    );

    const slider = screen.getByRole('slider');
    expect(slider).toBeDisabled();
  });
});