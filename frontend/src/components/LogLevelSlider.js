import React, { useState } from 'react';

const LOG_LEVELS = ['ERROR', 'WARN', 'INFO', 'DEBUG', 'TRACE'];

const LogLevelSlider = ({ value, onChange, label, disabled = false }) => {
  const [showTooltip, setShowTooltip] = useState(false);
  
  // Convert log level string to slider position (0-4)
  const getSliderPosition = (logLevel) => {
    const index = LOG_LEVELS.indexOf(logLevel);
    return index >= 0 ? index : 2; // Default to INFO if not found
  };
  
  // Convert slider position to log level string
  const getLogLevel = (position) => {
    return LOG_LEVELS[position] || 'INFO';
  };
  
  const currentPosition = getSliderPosition(value);
  
  const handleSliderChange = (event) => {
    const newPosition = parseInt(event.target.value, 10);
    const newLogLevel = getLogLevel(newPosition);
    onChange(newLogLevel);
  };
  
  const handleKeyDown = (event) => {
    let newPosition = currentPosition;
    
    switch (event.key) {
      case 'ArrowLeft':
      case 'ArrowDown':
        event.preventDefault();
        newPosition = Math.max(0, currentPosition - 1);
        break;
      case 'ArrowRight':
      case 'ArrowUp':
        event.preventDefault();
        newPosition = Math.min(4, currentPosition + 1);
        break;
      case 'Home':
        event.preventDefault();
        newPosition = 0;
        break;
      case 'End':
        event.preventDefault();
        newPosition = 4;
        break;
      default:
        return;
    }
    
    if (newPosition !== currentPosition) {
      onChange(getLogLevel(newPosition));
    }
  };
  
  return (
    <div className="log-level-slider-container">
      <label className="log-level-label">{label}</label>
      <div 
        className="slider-wrapper"
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        <input
          type="range"
          min="0"
          max="4"
          step="1"
          value={currentPosition}
          onChange={handleSliderChange}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          className="log-level-slider"
          aria-label={`${label} log level`}
          aria-valuetext={`${value} - Position ${currentPosition + 1} of 5`}
        />
        <div className="slider-track">
          <div className="slider-levels">
            {LOG_LEVELS.map((level, index) => (
              <div
                key={level}
                className={`slider-level ${index === currentPosition ? 'active' : ''}`}
                data-level={level}
              >
                {level}
              </div>
            ))}
          </div>
        </div>
        {showTooltip && (
          <div className="slider-tooltip">
            {value} (Position {currentPosition + 1}/5)
          </div>
        )}
      </div>
    </div>
  );
};

export default LogLevelSlider;