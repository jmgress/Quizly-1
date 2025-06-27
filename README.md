# 🧠 Quizly - Knowledge Testing Application

An interactive web-based quiz application that allows users to test their knowledge on various topics. Built with FastAPI backend and a responsive HTML/JavaScript frontend.

## Features

- 🎯 **Interactive Quiz Experience**: Multiple-choice questions with immediate feedback
- 📊 **Progress Tracking**: Visual progress bar and question counter
- 🏆 **Score Display**: Final score with percentage and performance message
- 📝 **Answer Review**: Detailed review of all answers after quiz completion
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 🎨 **Modern UI**: Clean, gradient-based design with smooth animations
- 🔄 **Multiple Categories**: Questions across geography, science, math, and literature
- 🎯 **Subject Selection**: Choose your preferred quiz category before starting
- 🤖 **AI-Powered Questions**: Generate fresh questions using Ollama LLM integration
- 📚 **Dual Question Sources**: Select between curated database questions or AI-generated content
- 🚀 **Fast API**: RESTful API with automatic documentation
- 🛠️ **Admin Panel**: Comprehensive admin interface with dual tabs for question management and system monitoring
- 📋 **Real-time Logging**: Comprehensive logging system with real-time log viewer in admin interface
- 🔍 **Log Filtering**: Filter logs by level, module, timestamp, with pagination support
- ⚙️ **Dynamic Log Configuration**: Change log levels on-the-fly through the admin interface

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for Python
- **SQLite**: Lightweight database for question storage
- **Ollama**: AI integration for question generation
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for running FastAPI

### Frontend
- **React**: Modern JavaScript library for building user interfaces
- **React Hooks**: For state management and component lifecycle
- **Axios**: HTTP client for API communication
- **CSS3**: Modern styling with responsive design

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm (Node Package Manager)
- Modern web browser

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Install Python dependencies:**
   ```bash
   # Option 1: Using pip
   pip install fastapi uvicorn
   
   # Option 2: Using system packages (Ubuntu/Debian)
   sudo apt install python3-fastapi python3-uvicorn
   ```

3. **Run the backend server:**
   ```bash
   python main.py
   ```
   
   The API will be available at `http://localhost:8000`
   
   **API Documentation:** Visit `http://localhost:8000/docs` for interactive API documentation

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the React development server:**
   ```bash
   npm start
   ```

4. **Open in browser:**
   Visit `http://localhost:3000`

The React dev server will automatically reload when you make changes to the code.

### Automated Setup (Recommended)

For the easiest setup, use the provided startup script that handles both backend and frontend:

```bash
./start.sh
```

This script will:
- Check for required dependencies (Python 3.8+, Node.js, npm)
- Install npm packages if needed
- Start both backend and frontend servers

### AI Question Generation Setup (Optional)

To enable AI-powered question generation, you need to install and configure Ollama:

1. **Install Ollama:**
   - Visit [ollama.ai](https://ollama.ai) and follow the installation instructions for your platform
   - Or use the command line:
     ```bash
     curl -fsSL https://ollama.ai/install.sh | sh
     ```

2. **Pull the required model:**
   ```bash
   ollama pull llama3.2
   ```

3. **Start Ollama service:**
   ```bash
   ollama serve
   ```

Once Ollama is running with the llama3.2 model, the AI question generation feature will work automatically. If Ollama is not available, users can still use curated database questions.

The startup script will also display the URLs where the application is running.

Press `Ctrl+C` to stop both servers when done.

## How to Use

1. **Start Quiz**: Click "Start Quiz" on the home screen
2. **Select Subject**: Choose your preferred quiz category (Geography, Science, Math, Literature)
3. **Choose Question Source**:
   - **📚 Curated Questions**: High-quality pre-written questions from the database
   - **🤖 AI-Generated Questions**: Fresh questions powered by Ollama (requires Ollama setup)
4. **Take Quiz**: Answer questions and see immediate feedback
5. **View Results**: Review your score and answer details at the end

### Admin Interface

The admin interface provides comprehensive tools for question management and system monitoring through a tabbed interface.

**Access the Admin Panel:**
1. Navigate to the Quizly homepage
2. Click the "Admin Panel" button, or
3. Go directly to `http://localhost:3000/#admin`

**Admin Panel Tabs:**

#### 📝 Question Management Tab
- **View All Questions**: See all questions with their options, correct answers, and categories
- **Edit Questions**: Click "Edit" on any question to modify:
  - Question text
  - Answer options (A, B, C, D)
  - Correct answer selection
  - Category assignment
- **Save Changes**: Click "Save" to update questions or "Cancel" to discard changes
- **Error Handling**: Validation ensures all required fields are filled and correct answers are valid

#### 📋 View Logs Tab
- **Real-time Log Viewer**: Monitor application logs with automatic refresh capabilities
- **Log Filtering**: Filter logs by:
  - Log level (DEBUG, INFO, WARNING, ERROR)
  - Module (API, Database, Quiz, Admin, AI, etc.)
  - Number of entries displayed (25, 50, 100, 200)
- **Auto-refresh**: Toggle 15-second auto-refresh for real-time monitoring
- **Log Level Configuration**: Dynamically change the application's log verbosity
- **Pagination**: Navigate through large sets of log entries
- **Message Expansion**: Expand long log messages for detailed viewing
- **Color-coded Levels**: Visual differentiation of log levels with color coding

**Admin Interface Features:**
- No authentication required (access via direct URL)
- Real-time feedback on save operations
- Mobile-responsive design for editing on any device
- Automatic validation of question format and correct answers
- Persistent log level preferences stored in browser localStorage

## API Endpoints

### Questions
- **GET** `/api/questions` - Get quiz questions (supports `?category=<category>&limit=<limit>`)
- **PUT** `/api/questions/{id}` - Update a question's content (admin endpoint)
- **GET** `/api/questions/ai` - Generate AI-powered questions (supports `?subject=<subject>&limit=<limit>`)
- **GET** `/api/categories` - Get available question categories

### Quiz Management
- **POST** `/api/quiz/submit` - Submit quiz answers and get results
- **GET** `/api/quiz/{quiz_id}` - Get quiz results by ID

### Logging System
- **GET** `/api/logs` - Get application logs with filtering and pagination
  - Query parameters:
    - `limit` (optional): Number of entries to return (default: 100)
    - `offset` (optional): Starting position for pagination (default: 0)
    - `level` (optional): Filter by log level (DEBUG, INFO, WARNING, ERROR)
    - `module` (optional): Filter by module name (api, database, quiz, admin, ai, etc.)
    - `start_time` (optional): Filter logs after this timestamp (ISO format)
    - `end_time` (optional): Filter logs before this timestamp (ISO format)
- **POST** `/api/logs/config` - Configure logging level dynamically
  - Body: `{"level": "DEBUG|INFO|WARNING|ERROR"}`

### Example API Usage

**Get Questions:**
```bash
curl http://localhost:8000/api/questions
```

**Get Questions by Category:**
```bash
curl "http://localhost:8000/api/questions?category=geography&limit=5"
```

**Generate AI Questions:**
```bash
curl "http://localhost:8000/api/questions/ai?subject=history&limit=3"
```

**Submit Quiz:**
```bash
curl -X POST http://localhost:8000/api/quiz/submit \
  -H "Content-Type: application/json" \
  -d '{"answers": [{"question_id": 1, "selected_answer": "c"}]}'
```

**Get Application Logs:**
```bash
curl "http://localhost:8000/api/logs?limit=50&level=ERROR"
```

**Get Logs with Filtering:**
```bash
curl "http://localhost:8000/api/logs?module=api&level=INFO&limit=20&offset=0"
```

**Change Log Level:**
```bash
curl -X POST http://localhost:8000/api/logs/config \
  -H "Content-Type: application/json" \
  -d '{"level": "DEBUG"}'
```

**Update Question (Admin):**
```bash
curl -X PUT http://localhost:8000/api/questions/1 \
  -H "Content-Type: application/json" \
  -d '{"text": "Updated question text?", "category": "updated_category"}'
```

## Logging System

Quizly includes a comprehensive logging system that provides visibility into application behavior and assists with debugging.

### Logging Configuration

**Log Levels:**
- `DEBUG`: Detailed information for diagnosing problems
- `INFO`: General information about application events (default)
- `WARNING`: Warning messages for unexpected but non-critical events
- `ERROR`: Error messages for serious problems

**Log Output:**
- **Console**: Real-time logs displayed in the terminal
- **File**: Rotating log files stored in `backend/quizly.log`
  - Maximum file size: 10MB
  - Backup files: 5 files retained
  - Automatic rotation when size limit is reached

**Database Storage:**
- All logs are stored in the SQLite database for query and filtering
- Structured format with timestamp, level, module, and message
- Accessible via the admin interface and API endpoints

### Log Format

Each log entry includes:
```
YYYY-MM-DD HH:MM:SS - quizly - <module> - <LEVEL> - <message>
```

**Modules tracked:**
- `startup`: Application initialization
- `database`: Database operations
- `api`: API request/response handling
- `quiz`: Quiz submission and scoring
- `admin`: Admin interface operations
- `ai`: AI question generation
- `logs`: Logging system operations
- `config`: Configuration changes

### Using the Log Viewer

The admin interface provides a powerful log viewer with:

1. **Real-time Monitoring**: Auto-refresh every 15 seconds
2. **Filtering Options**: Filter by log level, module, and time range
3. **Pagination**: Navigate through large log sets
4. **Message Expansion**: View full details of long log messages
5. **Dynamic Configuration**: Change log levels without restarting

**Access the Log Viewer:**
1. Navigate to the admin panel
2. Click the "📋 View Logs" tab
3. Use filters to find specific logs
4. Enable auto-refresh for real-time monitoring

### Log Level Configuration

You can change the log level dynamically through:

**Admin Interface:**
- Use the log level dropdown in the admin panel
- Changes take effect immediately
- Setting is remembered in browser localStorage

**API Endpoint:**
```bash
curl -X POST http://localhost:8000/api/logs/config \
  -H "Content-Type: application/json" \
  -d '{"level": "DEBUG"}'
```

**Environment Variable** (set before starting):
```bash
export QUIZLY_LOG_LEVEL=DEBUG
```

### Troubleshooting with Logs

**Common Log Patterns:**

- **API Errors**: Look for ERROR level logs in the `api` module
- **Database Issues**: Check `database` module logs
- **AI Generation Problems**: Monitor `ai` module for connection issues
- **Performance Issues**: Enable DEBUG level for detailed timing information

**Example Log Queries:**

- View only errors: Filter by level = ERROR
- Monitor API activity: Filter by module = api
- Debug AI issues: Filter by module = ai, level = DEBUG
- Recent activity: Set limit to 50, sort by newest first

## Database Schema

The application uses SQLite with the following tables:

**Questions Table:**
- `id` (INTEGER PRIMARY KEY)
- `text` (TEXT) - Question text
- `options` (TEXT) - JSON array of answer options
- `correct_answer` (TEXT) - ID of correct option
- `category` (TEXT) - Question category

**Quiz Sessions Table:**
- `id` (TEXT PRIMARY KEY) - Unique quiz session ID
- `total_questions` (INTEGER)
- `correct_answers` (INTEGER)
- `score_percentage` (REAL)
- `created_at` (TEXT) - ISO timestamp
- `answers` (TEXT) - JSON array of answer details

**Logs Table:**
- `id` (INTEGER PRIMARY KEY)
- `timestamp` (TEXT) - ISO timestamp of log entry
- `level` (TEXT) - Log level (DEBUG, INFO, WARNING, ERROR)
- `module` (TEXT) - Source module that generated the log
- `message` (TEXT) - Log message content
- `created_at` (DATETIME) - Database insertion timestamp

## Sample Questions

The application comes with 5 sample questions covering:
- 🌍 **Geography**: Capitals and geography facts
- 🔬 **Science**: Planets and scientific knowledge
- 🔢 **Math**: Basic arithmetic
- 📚 **Literature**: Classic authors and works

## Development

### Adding New Questions

You can add questions directly to the database or extend the initialization code in `backend/main.py`:

```python
sample_questions = [
    {
        "text": "Your question here?",
        "options": [
            {"id": "a", "text": "Option A"},
            {"id": "b", "text": "Option B"},
            {"id": "c", "text": "Option C"},
            {"id": "d", "text": "Option D"}
        ],
        "correct_answer": "a",  # ID of correct option
        "category": "your_category"
    }
]
```

### Testing the Backend

Run the test script to verify backend functionality:
```bash
cd backend
python test_backend.py
```

### Testing the Frontend

The frontend is configured with Jest and React Testing Library for unit testing. Tests are available for the core components.

**Running Tests:**
```bash
cd frontend
npm test
```

**Running Tests with Coverage:**
```bash
cd frontend
npm test -- --coverage --collectCoverageFrom="src/components/**/*.{js,jsx}"
```

**Running Tests in CI Mode (no watch):**
```bash
cd frontend
npm test -- --watchAll=false
```

**Test Files:**
- `src/components/__tests__/Question.test.js` - Tests for Question component
- `src/components/__tests__/ScoreDisplay.test.js` - Tests for ScoreDisplay component

**What's Tested:**
- Question component rendering and user interactions
- ScoreDisplay component score display and answer review functionality
- Component snapshots for visual regression testing
- Coverage targets: ≥80% for tested components

### CORS Configuration

The backend is configured to accept requests from `http://localhost:3000`. To change this, modify the CORS settings in `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Project Structure

```
Quizly-1/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── logger.py            # Comprehensive logging system
│   ├── requirements.txt     # Python dependencies
│   ├── test_backend.py      # Backend tests
│   ├── quiz.db             # SQLite database (auto-generated)
│   └── quizly.log          # Application log file (auto-generated)
├── frontend/
│   ├── package.json        # React dependencies
│   ├── public/             # Public assets
│   │   └── index.html      # HTML template for React
│   └── src/                # React components
│       ├── App.js          # Main App component
│       ├── index.js        # React entry point
│       ├── index.css       # Global styles
│       └── components/
│           ├── Quiz.js     # Quiz logic component
│           ├── Question.js # Question display component
│           ├── ScoreDisplay.js # Score display component
│           ├── AdminQuestions.js # Admin panel with tabs
│           └── LogViewer.js # Real-time log viewer
├── start.sh                # Application launcher
├── README.md
└── LICENSE
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Future Enhancements

- 👤 User authentication and profiles
- 📈 Quiz history and statistics
- 🏷️ Custom quiz categories
- ⏱️ Timed quizzes
- 🎮 Multiplayer quiz mode
- 📱 Progressive Web App (PWA) support
- 🌐 Internationalization
- 🔔 WebSocket-based real-time log streaming
- 📊 Advanced analytics and monitoring dashboards
- 🚨 Log-based alerting and notifications
