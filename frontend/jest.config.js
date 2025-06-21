module.exports = {
  testEnvironment: 'jsdom',
  collectCoverageFrom: ['src/components/**/*.{js,jsx}'],
  coverageThreshold: {
    './src/components/Question.js': { branches: 80, functions: 80, lines: 80 },
    './src/components/ScoreDisplay.js': { branches: 80, functions: 80, lines: 80 }
  }
};
