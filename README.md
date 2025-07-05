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
- 🤖 **AI-Powered Questions**: Generate fresh questions using multiple LLM providers
- 📚 **Dual Question Sources**: Select between curated database questions or AI-generated content
- 🔌 **Provider-Based Architecture**: Easy switching between Ollama and OpenAI providers
- ⚙️ **LLM Configuration via Admin Panel**: Configure LLM providers and models directly from the admin interface.
- ⚙️ **Environment Configuration**: Initial LLM setup via environment variables, overridable by admin panel settings.
- 🏥 **Health Checks**: Monitor LLM provider availability and status, visible in the admin panel.
- 🚀 **Fast API**: RESTful API with automatic documentation

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for Python
- **SQLite**: Lightweight database for question storage
- **LLM Providers**: Configurable AI integration supporting Ollama and OpenAI
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for running FastAPI
- **Python-dotenv**: Environment variable management

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

### LLM Provider Configuration

Quizly supports multiple LLM providers for AI question generation. Initial configuration can be set using environment variables, but these settings can be managed and overridden through the Admin Panel.

#### 1. Initial Environment Setup (Optional Fallback)

If `backend/llm_config.json` is not present, the application will fall back to using environment variables. Create a `.env` file in the project root directory (copy from `.env.example`):

```bash
cp .env.example .env
```

#### 2. Configure Your Preferred Provider (via Admin Panel)

The primary way to configure LLM providers and models is through the **Admin Panel**:
1. Navigate to `http://localhost:3000/#admin`.
2. Select the "LLM Settings" tab.
3. **Current Provider Display**: Shows the currently active provider and model.
4. **Provider Selection**: Choose between Ollama, OpenAI, or other configured providers.
5. **Model Selection**: Select a specific model, filtered by the chosen provider. Available models are dynamically listed.
6. **Health Check**: View the health status of each provider. You can refresh the health status.
7. **Save/Apply**: Click "Save Configuration" to apply your changes. The system will validate the provider's availability before saving.

The configuration is stored in `backend/llm_config.json` and will persist across application restarts.

#### 3. Provider-Specific Setup (Required for functionality)

Ensure the chosen LLM provider is correctly set up in your environment:

**Ollama Setup:**
1. Install Ollama from [ollama.ai](https://ollama.ai).
2. Pull desired models, e.g.:
   ```bash
   ollama pull llama3.2
   ollama pull codellama
   ```
3. Ensure the Ollama service is running (usually `ollama serve` or it runs as a background service).

**OpenAI Setup:**
1. Get your API key from [OpenAI](https://platform.openai.com/api-keys).
2. Ensure the `OPENAI_API_KEY` environment variable is set in your backend environment (e.g., in your `.env` file or system environment). The Admin Panel does not directly manage API keys.

#### 4. Health Check (via API or Admin Panel)

You can check the health of any provider via the API:
```bash
curl http://localhost:8000/api/llm/health?provider_name=ollama
curl http://localhost:8000/api/llm/health?provider_name=openai
```
If `provider_name` is omitted, it checks the currently configured provider.
The response includes provider status and available models:
```json
{
  "provider": "ollama",
  "healthy": true,
  "models": ["llama3.2:latest", "codellama:latest"]
}
```
Health status is also visible and refreshable in the Admin Panel's "LLM Settings" tab.

#### 5. Supported Environment Variables (for fallback and API keys)

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `LLM_PROVIDER` | Provider type: "ollama" or "openai" | ollama |
| `OLLAMA_MODEL` | Ollama model name | llama3.2 |
| `OLLAMA_HOST` | Ollama server URL | http://localhost:11434 |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `OPENAI_MODEL` | OpenAI model name | gpt-3.5-turbo |
| `DEFAULT_QUESTION_LIMIT` | Default number of questions | 5 |
| `LOG_LEVEL` | Logging level | INFO |

### AI Question Generation Setup (Optional)

To enable AI-powered question generation, you need to set up at least one LLM provider:

#### Option A: Ollama (Local/Free)

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

#### Option B: OpenAI (Cloud/Paid)

1. **Get an OpenAI API key:**
   - Visit [OpenAI Platform](https://platform.openai.com/api-keys)
   - Create a new API key

2. **Configure the environment:**
   ```bash
   echo "LLM_PROVIDER=openai" >> .env
   echo "OPENAI_API_KEY=your-actual-api-key" >> .env
   ```

Once configured, the AI question generation feature will work automatically. If no provider is available, users can still use curated database questions.

The startup script will also display the URLs where the application is running.

Press `Ctrl+C` to stop both servers when done.

## How to Use

1. **Start Quiz**: Click "Start Quiz" on the home screen
2. **Select Subject**: Choose your preferred quiz category (Geography, Science, Math, Literature)
3. **Choose Question Source**:
   - **📚 Curated Questions**: High-quality pre-written questions from the database
   - **🤖 AI-Generated Questions**: Fresh questions powered by your configured LLM provider (Ollama or OpenAI)
4. **Take Quiz**: Answer questions and see immediate feedback
5. **View Results**: Review your score and answer details at the end

### AI Question Generation

The AI question generation feature uses your configured LLM provider to create fresh, unique questions on any topic. The system will:

- Generate questions based on the selected subject
- Format them consistently with the existing question structure
- Provide appropriate difficulty levels
- Include proper multiple-choice options with correct answers

If AI generation fails (provider offline, API quota exceeded, etc.), the system will gracefully fall back to curated database questions.

### Admin Interface

The admin interface allows you to view and edit all quiz questions stored in the database.

**Access the Admin Panel:**
1. Navigate to the Quizly homepage
2. Click the "Admin Panel" button, or
3. Go directly to `http://localhost:3000/#admin`

**Admin Features:**
- **View All Questions**: (In "Manage Questions" tab) See all questions with their options, correct answers, and categories.
- **Edit Questions**: (In "Manage Questions" tab) Click "Edit" on any question to modify its text, options, correct answer, and category.
- **Save Changes**: (In "Manage Questions" tab) Click "Save" to update questions or "Cancel" to discard changes.
- **LLM Settings Management**: (In "LLM Settings" tab)
    - View current LLM provider and model.
    - Select and save a new LLM provider (e.g., Ollama, OpenAI).
    - Select and save a specific model for the chosen provider.
    - View health status of available LLM providers.
- **Error Handling**: Validation for question editing and LLM configuration.

**Admin Interface Usage:**
- No authentication required (access via direct URL).
- Real-time feedback on save operations for both questions and LLM settings.
- Mobile-responsive design.

## API Endpoints

### Questions
- **GET** `/api/questions` - Get quiz questions (supports `?category=<category>&limit=<limit>`)
- **PUT** `/api/questions/{id}` - Update a question's content (admin endpoint)
- **GET** `/api/questions/ai` - Generate AI-powered questions using the globally configured LLM provider and model (supports `?subject=<subject>&limit=<limit>`)
- **GET** `/api/categories` - Get available question categories

### LLM Provider Management
- **GET** `/api/llm/config` - Get the current LLM provider and model configuration.
- **POST** `/api/llm/config` - Set the LLM provider and model configuration.
  ```json
  {
    "provider": "ollama",
    "model": "llama3.2"
  }
  ```
- **GET** `/api/llm/health` - Check health of a specific or currently configured LLM provider (supports `?provider_name=<provider>`). Returns health status and available models for that provider.
- **GET** `/api/llm/providers` - Get a list of available providers, their health status, and their models.
- **GET** `/api/models` - List available models for a specific provider (supports `?provider=<provider>`).

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

**Check LLM Provider Health (specific provider):**
```bash
curl http://localhost:8000/api/llm/health?provider_name=ollama
```

**Get Current LLM Configuration:**
```bash
curl http://localhost:8000/api/llm/config
```

**Set LLM Configuration:**
```bash
curl -X POST http://localhost:8000/api/llm/config \
  -H "Content-Type: application/json" \
  -d '{"provider": "openai", "model": "gpt-4o-mini"}'
```

**Generate AI Questions (uses configured LLM settings):**
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
