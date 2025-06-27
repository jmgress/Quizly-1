"""
Quizly Logging System

A comprehensive logging module that provides configurable logging levels,
rotating file handlers, and structured log storage for the Quizly application.
"""

import logging
import logging.handlers
import json
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

class QuizlyLogger:
    """Main logger class for Quizly application with database storage"""
    
    def __init__(self, log_level: str = "INFO", log_file: str = "quizly.log"):
        self.log_file = log_file
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        
        # Setup logger
        self.logger = logging.getLogger("quizly")
        self.logger.setLevel(self.log_level)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Create formatters
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(module)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler with rotation (max 10MB, keep 5 files)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Initialize database storage
        self._init_log_db()
        
    def _init_log_db(self):
        """Initialize the log storage database"""
        conn = sqlite3.connect('quiz.db')
        cursor = conn.cursor()
        
        # Create logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                level TEXT NOT NULL,
                module TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def _log_to_db(self, level: str, module: str, message: str):
        """Store log entry in database"""
        try:
            conn = sqlite3.connect('quiz.db')
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO logs (timestamp, level, module, message) VALUES (?, ?, ?, ?)",
                (timestamp, level, module, message)
            )
            
            conn.commit()
            conn.close()
        except Exception as e:
            # Don't let logging errors break the application
            print(f"Failed to store log in database: {e}")
    
    def set_level(self, level: str):
        """Change logging level dynamically"""
        self.log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(self.log_level)
        for handler in self.logger.handlers:
            handler.setLevel(self.log_level)
    
    def info(self, message: str, module: str = "main"):
        """Log info message"""
        self.logger.info(message)
        self._log_to_db("INFO", module, message)
    
    def debug(self, message: str, module: str = "main"):
        """Log debug message"""
        self.logger.debug(message)
        self._log_to_db("DEBUG", module, message)
    
    def warning(self, message: str, module: str = "main"):
        """Log warning message"""
        self.logger.warning(message)
        self._log_to_db("WARNING", module, message)
    
    def error(self, message: str, module: str = "main"):
        """Log error message"""
        self.logger.error(message)
        self._log_to_db("ERROR", module, message)
    
    def get_logs(self, 
                 limit: int = 100, 
                 offset: int = 0,
                 level: Optional[str] = None,
                 module: Optional[str] = None,
                 start_time: Optional[str] = None,
                 end_time: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve logs from database with filtering and pagination"""
        
        conn = sqlite3.connect('quiz.db')
        cursor = conn.cursor()
        
        # Build query with filters
        query = "SELECT id, timestamp, level, module, message, created_at FROM logs WHERE 1=1"
        params = []
        
        if level:
            query += " AND level = ?"
            params.append(level.upper())
        
        if module:
            query += " AND module = ?"
            params.append(module)
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        
        query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Get total count for pagination
        count_query = "SELECT COUNT(*) FROM logs WHERE 1=1"
        count_params = []
        
        if level:
            count_query += " AND level = ?"
            count_params.append(level.upper())
        
        if module:
            count_query += " AND module = ?"
            count_params.append(module)
        
        if start_time:
            count_query += " AND timestamp >= ?"
            count_params.append(start_time)
        
        if end_time:
            count_query += " AND timestamp <= ?"
            count_params.append(end_time)
        
        cursor.execute(count_query, count_params)
        total_count = cursor.fetchone()[0]
        
        conn.close()
        
        logs = []
        for row in rows:
            logs.append({
                "id": row[0],
                "timestamp": row[1],
                "level": row[2],
                "module": row[3],
                "message": row[4],
                "created_at": row[5]
            })
        
        return {
            "logs": logs,
            "total": total_count,
            "limit": limit,
            "offset": offset
        }

# Global logger instance
quizly_logger = QuizlyLogger()

# Convenience functions for easy use
def info(message: str, module: str = "main"):
    quizly_logger.info(message, module)

def debug(message: str, module: str = "main"):
    quizly_logger.debug(message, module)

def warning(message: str, module: str = "main"):
    quizly_logger.warning(message, module)

def error(message: str, module: str = "main"):
    quizly_logger.error(message, module)

def set_log_level(level: str):
    quizly_logger.set_level(level)

def get_logs(**kwargs):
    return quizly_logger.get_logs(**kwargs)