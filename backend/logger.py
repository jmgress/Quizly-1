import logging
import logging.handlers
import os

LOG_LEVEL_STR = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_LEVEL = getattr(logging, LOG_LEVEL_STR, logging.INFO)

LOG_FILE = "quizly.log"
MAX_BYTES = 1024 * 1024  # 1 MB
BACKUP_COUNT = 5

def setup_logger(name="quizly"):
    """Configures and returns a logger."""
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    # Prevent duplicate handlers if logger is already configured
    if logger.hasHandlers():
        logger.handlers.clear()

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Rotating File Handler
    # Create log directory if it doesn't exist (though for quizly.log it's root)
    # For a real app, you might put logs in a 'logs' subdirectory.
    # os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True) # Not needed if LOG_FILE is in current dir

    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Default application logger
app_logger = setup_logger()

# Example usage (can be removed or commented out)
if __name__ == "__main__":
    test_logger = setup_logger("test_module")
    test_logger.debug("This is a debug message.")
    test_logger.info("This is an info message.")
    test_logger.warning("This is a warning message.")
    test_logger.error("This is an error message.")
    test_logger.critical("This is a critical message.")

    # Test log rotation by logging a lot of data
    # for i in range(20000):
    #    test_logger.info(f"Log entry {i} to test rotation.")
    print(f"Logging configured. Log level: {LOG_LEVEL_STR}. Log file: {LOG_FILE}")
