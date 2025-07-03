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

## Advanced Configuration: LLM Providers

Quizly now supports multiple Large Language Model (LLM) providers for AI question generation, allowing you to switch between Ollama and OpenAI, or configure them more granularly. This is managed through environment variables, typically set in a `.env` file at the root of the repository.

### Setting up the `.env` file

1.  **Create a `.env` file:** In the root directory of the project, create a file named `.env`.
2.  **Copy from example:** You can copy the contents of `.env.example` into your new `.env` file as a starting point.
    ```bash
    cp .env.example .env
    ```
3.  **Customize variables:** Edit the `.env` file with your desired settings.

### Environment Variables

The following environment variables control the LLM provider integration:

-   `LLM_PROVIDER`: Specifies the LLM provider to use.
    -   Values: `"ollama"` (default) or `"openai"`.
    -   Example: `LLM_PROVIDER="openai"`

-   `OLLAMA_API_HOST`: The host URL for your Ollama instance (if using Ollama).
    -   Default: `"http://localhost:11434"`
    -   Example: `OLLAMA_API_HOST="http://192.168.1.100:11434"`

-   `OLLAMA_MODEL`: The Ollama model to use for question generation.
    -   Default: `"mistral"` (ensure you have this model pulled via `ollama pull mistral`)
    -   Example: `OLLAMA_MODEL="llama3.2"`

-   `OPENAI_API_KEY`: Your API key for OpenAI (required if `LLM_PROVIDER="openai"`).
    -   Example: `OPENAI_API_KEY="sk-yourActualOpenAIkeyHere"`

-   `OPENAI_MODEL`: The OpenAI model to use.
    -   Default: `"gpt-3.5-turbo"`
    -   Example: `OPENAI_MODEL="gpt-4"`

-   `PROMPT_TEMPLATE`: The template string used to generate prompts for the LLM. This allows customization of how questions are requested.
    -   Available placeholders: `{subject}`, `{limit}`, `{subject_lowercase}`.
    -   The default template is designed to produce JSON-formatted questions and is defined in `backend/llm_providers.py`. You can override it in your `.env` file if needed, but ensure the output format remains compatible with the application's parser.
    -   Example (if you need to change it, ensure proper JSON escaping if putting this in `.env` directly for complex strings):
        ```
        PROMPT_TEMPLATE="Generate {limit} tricky multiple-choice questions about {subject}. Each question must have 4 options (a,b,c,d) and indicate the correct one. Output as a JSON list: [{\"text\":\"...\", \"options\":[{\"id\":\"a\",...},...], \"correct_answer\":\"a\", \"category\":\"{subject_lowercase}\"}]"
        ```

### Examples

**Using Ollama (default or explicit):**

If you have Ollama running locally and want to use the `llama3.2` model:
```env
# .env file content
LLM_PROVIDER="ollama"
OLLAMA_MODEL="llama3.2"
# OLLAMA_API_HOST defaults to http://localhost:11434 if not set
```

**Using OpenAI:**

If you want to use OpenAI with the `gpt-4` model:
```env
# .env file content
LLM_PROVIDER="openai"
OPENAI_API_KEY="your_openai_api_key_here"
OPENAI_MODEL="gpt-4"
```

**Note:** The backend server (`main.py`) needs to be restarted for changes in the `.env` file to take effect. The `python-dotenv` library loads these variables at application startup.

## How to Use

1. **Start Quiz**: Click "Start Quiz" on the home screen
2. **Select Subject**: Choose your preferred quiz category (Geography, Science, Math, Literature)
3. **Choose Question Source**:
   - **📚 Curated Questions**: High-quality pre-written questions from the database
   - **🤖 AI-Generated Questions**: Fresh questions powered by Ollama (requires Ollama setup)
4. **Take Quiz**: Answer questions and see immediate feedback
5. **View Results**: Review your score and answer details at the end

### Admin Interface

The admin interface allows you to view and edit all quiz questions stored in the database.

**Access the Admin Panel:**
1. Navigate to the Quizly homepage
2. Click the "Admin Panel" button, or
3. Go directly to `http://localhost:3000/#admin`

**Admin Features:**
- **View All Questions**: See all questions with their options, correct answers, and categories
- **Edit Questions**: Click "Edit" on any question to modify:
  - Question text
  - Answer options (A, B, C, D)
  - Correct answer selection
  - Category assignment
- **Save Changes**: Click "Save" to update questions or "Cancel" to discard changes
- **Error Handling**: Validation ensures all required fields are filled and correct answers are valid

**Admin Interface Usage:**
- No authentication required (access via direct URL)
- Real-time feedback on save operations
- Mobile-responsive design for editing on any device
- Automatic validation of question format and correct answers

## API Endpoints

### Questions
- **GET** `/api/questions` - Get quiz questions (supports `?category=<category>&limit=<limit>`)
- **PUT** `/api/questions/{id}` - Update a question's content (admin endpoint)
- **GET** `/api/questions/ai` - Generate AI-powered questions (supports `?subject=<subject>&limit=<limit>`)
- **GET** `/api/categories` - Get available question categories

### Quiz Management
- **POST** `/api/quiz/submit` - Submit quiz answers and get results
- **GET** `/api/quiz/{quiz_id}` - Get quiz results by ID

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

**Update Question (Admin):**
```bash
curl -X PUT http://localhost:8000/api/questions/1 \
  -H "Content-Type: application/json" \
  -d '{"text": "Updated question text?", "category": "updated_category"}'
```

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
│   ├── requirements.txt     # Python dependencies
│   ├── test_backend.py      # Backend tests
│   └── quiz.db             # SQLite database (auto-generated)
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
│           └── ScoreDisplay.js # Score display component
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
- 📊 Admin dashboard for question management
