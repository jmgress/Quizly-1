/**
 * Shared test helpers for JavaScript/React tests
 */

import { render } from '@testing-library/react';
import { jest } from '@jest/globals';

/**
 * Create mock axios instance for testing
 */
export const createMockAxios = () => {
  return {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    patch: jest.fn(),
    defaults: {
      headers: {
        common: {}
      }
    }
  };
};

/**
 * Mock question data for testing
 */
export const mockQuestions = [
  {
    id: 1,
    text: 'What is the capital of France?',
    options: [
      { id: 'a', text: 'London' },
      { id: 'b', text: 'Berlin' },
      { id: 'c', text: 'Paris' },
      { id: 'd', text: 'Madrid' }
    ],
    correct_answer: 'c',
    category: 'geography'
  },
  {
    id: 2,
    text: 'What is 2 + 2?',
    options: [
      { id: 'a', text: '3' },
      { id: 'b', text: '4' },
      { id: 'c', text: '5' },
      { id: 'd', text: '6' }
    ],
    correct_answer: 'b',
    category: 'math'
  },
  {
    id: 3,
    text: 'Which programming language is used for web development?',
    options: [
      { id: 'a', text: 'Python' },
      { id: 'b', text: 'JavaScript' },
      { id: 'c', text: 'Java' },
      { id: 'd', text: 'C++' }
    ],
    correct_answer: 'b',
    category: 'programming'
  }
];

/**
 * Mock AI-generated questions
 */
export const mockAIQuestions = [
  {
    text: 'What is machine learning?',
    options: [
      { id: 'a', text: 'A type of computer hardware' },
      { id: 'b', text: 'A subset of artificial intelligence' },
      { id: 'c', text: 'A programming language' },
      { id: 'd', text: 'A database system' }
    ],
    correct_answer: 'b',
    category: 'technology'
  }
];

/**
 * Mock quiz results
 */
export const mockQuizResults = {
  totalQuestions: 3,
  correctAnswers: 2,
  scorePercentage: 66.67,
  answers: [
    { questionId: 1, selectedAnswer: 'c', isCorrect: true },
    { questionId: 2, selectedAnswer: 'a', isCorrect: false },
    { questionId: 3, selectedAnswer: 'b', isCorrect: true }
  ]
};

/**
 * Mock configuration data
 */
export const mockConfig = {
  llmProvider: 'openai',
  openaiModel: 'gpt-3.5-turbo',
  ollamaModel: 'llama3.2',
  ollamaHost: 'http://localhost:11434'
};

/**
 * Mock logging configuration
 */
export const mockLoggingConfig = {
  level: 'INFO',
  format: '%(asctime)s - %(levelname)s - %(message)s',
  handlers: {
    file: {
      filename: 'app.log',
      maxBytes: 1024000,
      backupCount: 3
    },
    console: {
      stream: 'stdout'
    }
  }
};

/**
 * Create a test question with default values
 */
export const createTestQuestion = ({
  id = 1,
  text = 'Test question?',
  category = 'test',
  correctAnswer = 'a',
  options = [
    { id: 'a', text: 'Option A' },
    { id: 'b', text: 'Option B' },
    { id: 'c', text: 'Option C' },
    { id: 'd', text: 'Option D' }
  ]
} = {}) => {
  return {
    id,
    text,
    category,
    correct_answer: correctAnswer,
    options
  };
};

/**
 * Create mock API responses
 */
export const createMockApiResponse = (data, status = 200) => {
  return {
    data,
    status,
    statusText: status === 200 ? 'OK' : 'Error',
    headers: {},
    config: {}
  };
};

/**
 * Create mock error response
 */
export const createMockErrorResponse = (message = 'API Error', status = 500) => {
  const error = new Error(message);
  error.response = {
    status,
    statusText: 'Error',
    data: { error: message }
  };
  return Promise.reject(error);
};

/**
 * Validate question structure
 */
export const validateQuestionStructure = (question) => {
  const requiredFields = ['text', 'options', 'correct_answer'];
  
  for (const field of requiredFields) {
    if (!(field in question)) {
      return false;
    }
  }
  
  if (!Array.isArray(question.options) || question.options.length === 0) {
    return false;
  }
  
  for (const option of question.options) {
    if (!('id' in option) || !('text' in option)) {
      return false;
    }
  }
  
  // Check that correct_answer references a valid option
  const optionIds = question.options.map(opt => opt.id);
  if (!optionIds.includes(question.correct_answer)) {
    return false;
  }
  
  return true;
};

/**
 * Calculate quiz score
 */
export const calculateQuizScore = (answers) => {
  if (!answers || answers.length === 0) {
    return 0;
  }
  
  const correctCount = answers.filter(answer => answer.isCorrect).length;
  return (correctCount / answers.length) * 100;
};

/**
 * Wait for async operations in tests
 */
export const waitFor = (condition, timeout = 5000) => {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    
    const check = () => {
      if (condition()) {
        resolve();
      } else if (Date.now() - startTime > timeout) {
        reject(new Error(`Timeout waiting for condition after ${timeout}ms`));
      } else {
        setTimeout(check, 100);
      }
    };
    
    check();
  });
};

/**
 * Mock local storage for testing
 */
export const createMockLocalStorage = () => {
  let store = {};
  
  return {
    getItem: jest.fn((key) => store[key] || null),
    setItem: jest.fn((key, value) => {
      store[key] = value.toString();
    }),
    removeItem: jest.fn((key) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    }),
    get length() {
      return Object.keys(store).length;
    },
    key: jest.fn((index) => Object.keys(store)[index] || null)
  };
};

/**
 * Mock session storage for testing
 */
export const createMockSessionStorage = () => {
  return createMockLocalStorage(); // Same interface
};

/**
 * Setup global mocks for tests
 */
export const setupGlobalMocks = () => {
  // Mock window.localStorage
  Object.defineProperty(window, 'localStorage', {
    value: createMockLocalStorage(),
    writable: true
  });
  
  // Mock window.sessionStorage
  Object.defineProperty(window, 'sessionStorage', {
    value: createMockSessionStorage(),
    writable: true
  });
  
  // Mock window.location
  delete window.location;
  window.location = {
    href: 'http://localhost:3000',
    origin: 'http://localhost:3000',
    protocol: 'http:',
    host: 'localhost:3000',
    hostname: 'localhost',
    port: '3000',
    pathname: '/',
    search: '',
    hash: '',
    assign: jest.fn(),
    replace: jest.fn(),
    reload: jest.fn()
  };
  
  // Mock console methods to reduce noise in tests
  global.console = {
    ...console,
    warn: jest.fn(),
    error: jest.fn(),
    log: jest.fn()
  };
};

/**
 * Cleanup after tests
 */
export const cleanupAfterTests = () => {
  jest.clearAllMocks();
  jest.restoreAllMocks();
};

/**
 * Custom render function with common providers
 */
export const renderWithProviders = (ui, options = {}) => {
  // In a real app, you might wrap with providers like:
  // - React Router
  // - Redux/Context providers
  // - Theme providers
  // - Error boundaries
  
  const Wrapper = ({ children }) => {
    // Add providers here as needed
    return children;
  };
  
  return render(ui, { wrapper: Wrapper, ...options });
};

/**
 * Common test categories
 */
export const testCategories = [
  'geography',
  'math', 
  'programming',
  'science',
  'technology',
  'history'
];

/**
 * API endpoints for testing
 */
export const apiEndpoints = {
  questions: '/api/questions',
  aiQuestions: '/api/questions/ai',
  categories: '/api/categories',
  loggingConfig: '/api/logging/config',
  llmConfig: '/api/llm/config',
  health: '/api/health'
};

// Export all helpers
export default {
  createMockAxios,
  mockQuestions,
  mockAIQuestions,
  mockQuizResults,
  mockConfig,
  mockLoggingConfig,
  createTestQuestion,
  createMockApiResponse,
  createMockErrorResponse,
  validateQuestionStructure,
  calculateQuizScore,
  waitFor,
  createMockLocalStorage,
  createMockSessionStorage,
  setupGlobalMocks,
  cleanupAfterTests,
  renderWithProviders,
  testCategories,
  apiEndpoints
};