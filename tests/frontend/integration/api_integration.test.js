import axios from 'axios';

// Mock axios for testing
jest.mock('axios');
const mockedAxios = axios;

describe('API Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Questions API', () => {
    it('should fetch questions from database', async () => {
      const mockQuestions = [
        {
          id: 1,
          text: 'Test question',
          options: [
            { id: 'a', text: 'Option A' },
            { id: 'b', text: 'Option B' }
          ],
          correct_answer: 'a',
          category: 'test'
        }
      ];

      mockedAxios.get.mockResolvedValueOnce({ data: mockQuestions });

      const response = await axios.get('http://localhost:8000/api/questions?category=test');
      
      expect(response.data).toEqual(mockQuestions);
      expect(mockedAxios.get).toHaveBeenCalledWith('http://localhost:8000/api/questions?category=test');
    });

    it('should fetch AI-generated questions', async () => {
      const mockAIQuestions = [
        {
          text: 'AI generated question',
          options: [
            { id: 'a', text: 'AI Option A' },
            { id: 'b', text: 'AI Option B' }
          ],
          correct_answer: 'a',
          category: 'ai-generated'
        }
      ];

      mockedAxios.get.mockResolvedValueOnce({ data: mockAIQuestions });

      const response = await axios.get('http://localhost:8000/api/questions/ai?subject=python&limit=10');
      
      expect(response.data).toEqual(mockAIQuestions);
      expect(mockedAxios.get).toHaveBeenCalledWith('http://localhost:8000/api/questions/ai?subject=python&limit=10');
    });

    it('should handle API errors gracefully', async () => {
      mockedAxios.get.mockRejectedValueOnce(new Error('Network error'));

      try {
        await axios.get('http://localhost:8000/api/questions');
        fail('Should have thrown an error');
      } catch (error) {
        expect(error.message).toBe('Network error');
      }
    });
  });

  describe('Configuration API', () => {
    it('should fetch logging configuration', async () => {
      const mockLoggingConfig = {
        level: 'INFO',
        format: '%(asctime)s - %(levelname)s - %(message)s'
      };

      mockedAxios.get.mockResolvedValueOnce({ data: mockLoggingConfig });

      const response = await axios.get('http://localhost:8000/api/logging/config');
      
      expect(response.data).toEqual(mockLoggingConfig);
    });

    it('should update logging configuration', async () => {
      const newConfig = {
        level: 'DEBUG',
        format: '%(levelname)s - %(message)s'
      };

      mockedAxios.post.mockResolvedValueOnce({ data: newConfig });

      const response = await axios.post('http://localhost:8000/api/logging/config', newConfig);
      
      expect(response.data).toEqual(newConfig);
      expect(mockedAxios.post).toHaveBeenCalledWith('http://localhost:8000/api/logging/config', newConfig);
    });

    it('should fetch LLM configuration', async () => {
      const mockLLMConfig = {
        provider: 'openai',
        model: 'gpt-3.5-turbo'
      };

      mockedAxios.get.mockResolvedValueOnce({ data: mockLLMConfig });

      const response = await axios.get('http://localhost:8000/api/llm/config');
      
      expect(response.data).toEqual(mockLLMConfig);
    });
  });

  describe('Categories API', () => {
    it('should fetch available categories', async () => {
      const mockCategories = ['math', 'science', 'geography', 'programming'];

      mockedAxios.get.mockResolvedValueOnce({ data: mockCategories });

      const response = await axios.get('http://localhost:8000/api/categories');
      
      expect(response.data).toEqual(mockCategories);
    });
  });

  describe('Error Handling', () => {
    it('should handle 404 errors', async () => {
      mockedAxios.get.mockRejectedValueOnce({
        response: {
          status: 404,
          data: { error: 'Not found' }
        }
      });

      try {
        await axios.get('http://localhost:8000/api/nonexistent');
        fail('Should have thrown an error');
      } catch (error) {
        expect(error.response.status).toBe(404);
        expect(error.response.data.error).toBe('Not found');
      }
    });

    it('should handle 500 errors', async () => {
      mockedAxios.get.mockRejectedValueOnce({
        response: {
          status: 500,
          data: { error: 'Internal server error' }
        }
      });

      try {
        await axios.get('http://localhost:8000/api/questions');
        fail('Should have thrown an error');
      } catch (error) {
        expect(error.response.status).toBe(500);
        expect(error.response.data.error).toBe('Internal server error');
      }
    });

    it('should handle network timeouts', async () => {
      mockedAxios.get.mockRejectedValueOnce({
        code: 'ECONNABORTED',
        message: 'timeout of 5000ms exceeded'
      });

      try {
        await axios.get('http://localhost:8000/api/questions');
        fail('Should have thrown an error');
      } catch (error) {
        expect(error.code).toBe('ECONNABORTED');
        expect(error.message).toContain('timeout');
      }
    });
  });

  // TODO: Add more comprehensive API integration tests
  // - Test authentication endpoints (if implemented)
  // - Test admin endpoints with proper permissions
  // - Test rate limiting and throttling
  // - Test concurrent requests
  // - Test request/response interceptors
});