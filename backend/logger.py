import logging
from logging.handlers import RotatingFileHandler
import os

LOG_FILE = os.path.join(os.path.dirname(__file__), 'quizly.log')
DEFAULT_LEVEL = os.environ.get('QUIZLY_LOG_LEVEL', 'INFO').upper()


def configure_logging(level: str = DEFAULT_LEVEL):
    """Configure root logger with console and rotating file handlers."""
    logger = logging.getLogger()
    logger.setLevel(level)

    if not logger.handlers:
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
        file_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)


configure_logging()


def set_level(level: str):
    level = level.upper()
    logging.getLogger().setLevel(level)


def get_level() -> str:
    return logging.getLevelName(logging.getLogger().level)


def get_logs(level: str | None = None, start: str | None = None, end: str | None = None,
             module: str | None = None, limit: int = 100, offset: int = 0):
    """Read log entries from the log file with optional filtering."""
    entries = []
    if not os.path.exists(LOG_FILE):
        return []
    level = level.upper() if level else None

    with open(LOG_FILE, 'r') as f:
        lines = f.readlines()

    for line in lines:
        try:
            timestamp_part, rest = line.split(' [', 1)
            level_part, rest = rest.split('] ', 1)
            module_part, message = rest.split(': ', 1)
            entry = {
                'timestamp': timestamp_part.strip(),
                'level': level_part.strip(),
                'module': module_part.strip(),
                'message': message.strip(),
            }
        except ValueError:
            continue

        if level and entry['level'] != level:
            continue
        if module and module not in entry['module']:
            continue
        if start and entry['timestamp'] < start:
            continue
        if end and entry['timestamp'] > end:
            continue
        entries.append(entry)

    entries = entries[offset: offset + limit]
    return entries
