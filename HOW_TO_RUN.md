# How to Run Quizly Application

## Overview
Quizly is a full-stack knowledge testing application with a FastAPI backend (Python, SQLite) and a React frontend. This guide provides step-by-step instructions for setting up and running the application locally.

## Prerequisites

### System Requirements
- **Python 3.9+** (for backend)
- **Node.js 16+** and **npm** (for frontend)
- **Git** (for repository management)
- **Terminal/Command Line** access

### Optional Tools
- **Ollama** (for local AI question generation)
- **OpenAI API key** (for OpenAI-powered question generation)

## Quick Start (Recommended)

### 1. Clone the Repository
```bash
git clone https://github.com/jmgress/Quizly-1.git
cd Quizly-1
```

### 2. One-Command Setup and Run
```bash
./start.sh
```

This script will:
- Install backend dependencies
- Install frontend dependencies  
- Start both backend and frontend servers
- Open the application in your browser

**Access Points:**
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## Manual Setup (Step-by-Step)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment:**
   - **Linux/Mac:** `source venv/bin/activate`
   - **Windows:** `venv\Scripts\activate`

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Start backend server:**
   ```bash
   python main.py
   ```

The backend server will start on http://localhost:8000

### Frontend Setup

1. **Open new terminal and navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start frontend development server:**
   ```bash
   npm start
   ```

The frontend will start on http://localhost:3000 and automatically open in your browser.

## Configuration

### LLM Providers Setup

#### Option 1: Ollama (Local AI)
1. **Install Ollama:** Visit https://ollama.ai/download
2. **Start Ollama service:**
   ```bash
   ollama serve
   ```
3. **Pull a model:**
   ```bash
   ollama pull llama2
   ```
4. **Configure in app:** Go to Admin Panel → LLM Settings → Select "Ollama"

#### Option 2: OpenAI API
1. **Get API key:** Visit https://platform.openai.com/api-keys
2. **Configure in app:** Go to Admin Panel → LLM Settings → Enter API key

### Environment Variables (Optional)
Create a `.env` file in the backend directory:
```bash
# Server Configuration
APP_HOST=0.0.0.0
APP_PORT=8000

# LLM Configuration
OPENAI_API_KEY=your_openai_api_key_here
DEFAULT_QUESTION_LIMIT=5

# Database Configuration
DATABASE_PATH=quiz.db
```

## Using the Application

### 1. Taking a Quiz
1. Open http://localhost:3000
2. Select a subject or category
3. Answer the questions
4. View your results and score

### 2. Admin Features
1. Navigate to **Admin Panel** (button in main interface)
2. **Manage Questions:** Edit existing questions or add new ones
3. **LLM Settings:** Configure AI question generation
4. **Logging Settings:** Adjust application logging levels

### 3. AI Question Generation
1. Go to **Admin Panel → LLM Settings**
2. Configure your preferred AI provider (Ollama or OpenAI)
3. Test the connection with "Health Check"
4. Generate questions by selecting a subject and clicking "Generate AI Questions"

## Testing

### Run All Tests
```bash
./run_tests.sh
```

### Individual Test Suites

**Backend Tests:**
```bash
cd backend
pytest
```

**Frontend Tests:**
```bash
cd frontend
npm test
```

**Security Tests:**
```bash
./scripts/test_gitleaks.sh
```

## Troubleshooting

### Common Issues

#### Backend Won't Start
- **Check Python version:** `python --version` (should be 3.9+)
- **Verify virtual environment:** Ensure it's activated
- **Install dependencies:** `pip install -r requirements.txt`
- **Check logs:** Look in `logs/backend/` directory

#### Frontend Won't Start  
- **Check Node version:** `node --version` (should be 16+)
- **Clear cache:** `npm cache clean --force`
- **Reinstall dependencies:** `rm -rf node_modules && npm install`
- **Check port availability:** Ensure port 3000 is free

#### AI Features Not Working
- **Ollama:** Ensure service is running (`ollama serve`)
- **OpenAI:** Verify API key is valid and has sufficient credits
- **Network:** Check firewall/proxy settings

#### Database Issues
- **Reset database:** Delete `backend/quiz.db` (will recreate with sample data)
- **Check permissions:** Ensure write access to backend directory

### Log Files
Application logs are stored in the `logs/` directory:
- **Backend logs:** `logs/backend/api.log`, `logs/backend/error.log`
- **Frontend logs:** Browser console and `logs/frontend/`

### Port Configuration
- **Backend:** Change `APP_PORT` in `.env` or use `--port` flag
- **Frontend:** Set `PORT` environment variable: `PORT=3001 npm start`

## Architecture Overview

```
Quizly Application
├── Backend (FastAPI)
│   ├── REST API endpoints
│   ├── SQLite database
│   ├── LLM integrations (Ollama/OpenAI)
│   └── Logging system
├── Frontend (React)
│   ├── Quiz interface
│   ├── Admin panel
│   └── Settings management
└── Tests
    ├── Backend tests (pytest)
    ├── Frontend tests (Jest)
    └── Integration tests
```

## Additional Resources

- **Project Documentation:** See `docs/` directory
- **API Documentation:** http://localhost:8000/docs (when backend is running)
- **Testing Guide:** `docs/TESTING_GUIDE.md`
- **Architecture Details:** `docs/README.md`
- **GitHub Repository:** https://github.com/jmgress/Quizly-1

## Support

For issues and questions:
1. Check this guide first
2. Review logs in the `logs/` directory
3. Consult the `docs/` directory for detailed information
4. Check GitHub Issues for known problems

---

*Last updated: October 19, 2025*