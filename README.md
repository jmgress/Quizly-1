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
- 🚀 **Fast API**: RESTful API with automatic documentation

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for Python
- **SQLite**: Lightweight database for question storage
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for running FastAPI

### Frontend
- **HTML5/CSS3**: Semantic markup and modern styling
- **Vanilla JavaScript**: Interactive quiz functionality
- **Fetch API**: Communication with backend
- **CSS Grid/Flexbox**: Responsive layout

## Quick Start

### Prerequisites
- Python 3.8+
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

2. **Serve the frontend:**
   ```bash
   # Option 1: Using Python's built-in server
   python3 -m http.server 3000
   
   # Option 2: Using Node.js (if available)
   npx serve -p 3000
   ```

3. **Open in browser:**
   Visit `http://localhost:3000/index.html`

## API Endpoints

### Questions
- **GET** `/api/questions` - Get quiz questions (supports `?category=<category>&limit=<limit>`)
- **GET** `/api/categories` - Get available question categories

### Quiz Management
- **POST** `/api/quiz/submit` - Submit quiz answers and get results
- **GET** `/api/quiz/{quiz_id}` - Get quiz results by ID

### Example API Usage

**Get Questions:**
```bash
curl http://localhost:8000/api/questions
```

**Submit Quiz:**
```bash
curl -X POST http://localhost:8000/api/quiz/submit \
  -H "Content-Type: application/json" \
  -d '{"answers": [{"question_id": 1, "selected_answer": "c"}]}'
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
│   ├── index.html          # Main application
│   ├── package.json        # React dependencies (optional)
│   └── src/                # React components (optional)
│       ├── App.js
│       ├── index.js
│       ├── index.css
│       └── components/
│           ├── Quiz.js
│           ├── Question.js
│           └── ScoreDisplay.js
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
