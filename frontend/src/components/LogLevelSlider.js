import React from 'react';

const LOG_LEVELS = ['ERROR', 'WARN', 'INFO', 'DEBUG', 'TRACE'];

const LogLevelSlider = ({ currentLevel, onChange, label }) => {
  const currentLevelIndex = LOG_LEVELS.indexOf(currentLevel);

  const handleSliderChange = (event) => {
    const newIndex = parseInt(event.target.value, 10);
    onChange(LOG_LEVELS[newIndex]);
  };

  return (
    <div className="log-level-slider-container">
      {label && <label className="log-level-slider-label">{label}:</label>}
      <div className="slider-wrapper">
        <input
          type="range"
          min="0"
          max={LOG_LEVELS.length - 1}
          value={currentLevelIndex}
          onChange={handleSliderChange}
          className="log-level-slider"
          title={currentLevel} // Basic tooltip
          aria-label={`${label} log level`}
          aria-valuetext={currentLevel}
        />
        <div className="log-level-value">{currentLevel}</div>
      </div>
      <div className="log-level-markers">
        {LOG_LEVELS.map((level, index) => (
          <span key={level} className="log-level-marker" style={{ left: `${(index / (LOG_LEVELS.length -1)) * 100}%` }}>
            {level}
          </span>
        ))}
      </div>
    </div>
  );
};

export default LogLevelSlider;
