"""Mock server for testing API endpoints."""

import json
import sqlite3
import tempfile
from typing import Dict, List, Any, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
import urllib.parse

class MockQuizlyServer:
    """Mock server that simulates the Quizly backend API."""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.server = None
        self.server_thread = None
        self.db_path = ":memory:"
        self.setup_database()
    
    def setup_database(self):
        """Set up mock database with test data."""
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.connection.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                category TEXT NOT NULL,
                correct_answer TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE options (
                id TEXT NOT NULL,
                question_id INTEGER NOT NULL,
                text TEXT NOT NULL
            )
        ''')
        
        # Insert sample data
        sample_questions = [
            ("What is the capital of France?", "geography", "c"),
            ("What is 2 + 2?", "math", "b"),
            ("Which language is used for web development?", "programming", "b")
        ]
        
        for text, category, correct_answer in sample_questions:
            cursor.execute(
                "INSERT INTO questions (text, category, correct_answer) VALUES (?, ?, ?)",
                (text, category, correct_answer)
            )
            question_id = cursor.lastrowid
            
            # Add options based on question
            if "France" in text:
                options = [("a", "London"), ("b", "Berlin"), ("c", "Paris"), ("d", "Madrid")]
            elif "2 + 2" in text:
                options = [("a", "3"), ("b", "4"), ("c", "5"), ("d", "6")]
            else:
                options = [("a", "Python"), ("b", "JavaScript"), ("c", "Java"), ("d", "C++")]
            
            for opt_id, opt_text in options:
                cursor.execute(
                    "INSERT INTO options (id, question_id, text) VALUES (?, ?, ?)",
                    (opt_id, question_id, opt_text)
                )
        
        self.connection.commit()
    
    def start(self):
        """Start the mock server."""
        handler = self._create_handler()
        self.server = HTTPServer(('localhost', self.port), handler)
        
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # Wait a bit for server to start
        time.sleep(0.1)
    
    def stop(self):
        """Stop the mock server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        
        if self.server_thread:
            self.server_thread.join(timeout=1)
        
        if self.connection:
            self.connection.close()
    
    def _create_handler(self):
        """Create the request handler class."""
        mock_server = self
        
        class MockHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self._handle_get_request()
            
            def do_POST(self):
                self._handle_post_request()
            
            def do_OPTIONS(self):
                self._send_cors_headers()
                self.end_headers()
            
            def _handle_get_request(self):
                """Handle GET requests."""
                parsed_path = urllib.parse.urlparse(self.path)
                path = parsed_path.path
                query = urllib.parse.parse_qs(parsed_path.query)
                
                if path == '/api/health':
                    self._send_json_response({'status': 'ok'})
                
                elif path == '/api/questions':
                    category = query.get('category', [None])[0]
                    limit = int(query.get('limit', [10])[0])
                    questions = mock_server._get_questions(category, limit)
                    self._send_json_response(questions)
                
                elif path == '/api/questions/ai':
                    subject = query.get('subject', ['general'])[0]
                    limit = int(query.get('limit', [10])[0])
                    model = query.get('model', ['gpt-3.5-turbo'])[0]
                    ai_questions = mock_server._generate_ai_questions(subject, limit, model)
                    self._send_json_response(ai_questions)
                
                elif path == '/api/categories':
                    categories = mock_server._get_categories()
                    self._send_json_response(categories)
                
                elif path == '/api/logging/config':
                    config = mock_server._get_logging_config()
                    self._send_json_response(config)
                
                elif path == '/api/llm/config':
                    config = mock_server._get_llm_config()
                    self._send_json_response(config)
                
                else:
                    self._send_error_response(404, 'Not Found')
            
            def _handle_post_request(self):
                """Handle POST requests."""
                parsed_path = urllib.parse.urlparse(self.path)
                path = parsed_path.path
                
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length).decode('utf-8')
                
                try:
                    data = json.loads(post_data) if post_data else {}
                except json.JSONDecodeError:
                    self._send_error_response(400, 'Invalid JSON')
                    return
                
                if path == '/api/logging/config':
                    config = mock_server._update_logging_config(data)
                    self._send_json_response(config)
                
                elif path == '/api/llm/config':
                    config = mock_server._update_llm_config(data)
                    self._send_json_response(config)
                
                else:
                    self._send_error_response(404, 'Not Found')
            
            def _send_json_response(self, data: Any, status: int = 200):
                """Send JSON response."""
                self._send_cors_headers()
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                response = json.dumps(data, indent=2)
                self.wfile.write(response.encode('utf-8'))
            
            def _send_error_response(self, status: int, message: str):
                """Send error response."""
                self._send_cors_headers()
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                error_response = json.dumps({
                    'error': message,
                    'status_code': status
                })
                self.wfile.write(error_response.encode('utf-8'))
            
            def _send_cors_headers(self):
                """Send CORS headers."""
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            
            def log_message(self, format, *args):
                """Override to suppress log messages in tests."""
                pass
        
        return MockHandler
    
    def _get_questions(self, category: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get questions from mock database."""
        cursor = self.connection.cursor()
        
        if category:
            cursor.execute(
                "SELECT id, text, category, correct_answer FROM questions WHERE category = ? LIMIT ?",
                (category, limit)
            )
        else:
            cursor.execute(
                "SELECT id, text, category, correct_answer FROM questions LIMIT ?",
                (limit,)
            )
        
        questions = []
        for row in cursor.fetchall():
            question = {
                "id": row[0],
                "text": row[1],
                "category": row[2],
                "correct_answer": row[3]
            }
            
            # Get options
            cursor.execute(
                "SELECT id, text FROM options WHERE question_id = ?",
                (question["id"],)
            )
            question["options"] = [
                {"id": opt_row[0], "text": opt_row[1]}
                for opt_row in cursor.fetchall()
            ]
            
            questions.append(question)
        
        return questions
    
    def _generate_ai_questions(self, subject: str, limit: int, model: str) -> List[Dict]:
        """Generate mock AI questions."""
        # Simulate AI question generation
        ai_questions = []
        for i in range(limit):
            question = {
                "text": f"AI generated question about {subject} #{i+1}?",
                "options": [
                    {"id": "a", "text": f"Option A for {subject}"},
                    {"id": "b", "text": f"Option B for {subject}"},
                    {"id": "c", "text": f"Option C for {subject}"},
                    {"id": "d", "text": f"Option D for {subject}"}
                ],
                "correct_answer": "b",
                "category": "ai-generated"
            }
            ai_questions.append(question)
        
        return ai_questions
    
    def _get_categories(self) -> List[str]:
        """Get available question categories."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT DISTINCT category FROM questions")
        return [row[0] for row in cursor.fetchall()]
    
    def _get_logging_config(self) -> Dict:
        """Get mock logging configuration."""
        return {
            "level": "INFO",
            "format": "%(asctime)s - %(levelname)s - %(message)s",
            "handlers": {
                "file": {"filename": "app.log"},
                "console": {"stream": "stdout"}
            }
        }
    
    def _update_logging_config(self, config: Dict) -> Dict:
        """Update mock logging configuration."""
        # In a real implementation, this would update the actual config
        return {**self._get_logging_config(), **config}
    
    def _get_llm_config(self) -> Dict:
        """Get mock LLM configuration."""
        return {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "available_providers": ["openai", "ollama"]
        }
    
    def _update_llm_config(self, config: Dict) -> Dict:
        """Update mock LLM configuration."""
        # In a real implementation, this would update the actual config
        return {**self._get_llm_config(), **config}

# Convenience function for tests
def start_mock_server(port: int = 8080) -> MockQuizlyServer:
    """Start a mock server for testing."""
    server = MockQuizlyServer(port)
    server.start()
    return server

if __name__ == "__main__":
    # Example usage
    server = start_mock_server(8080)
    print(f"Mock server running on http://localhost:8080")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.stop()
        print("Server stopped.")