import json
import logging
import colorlog

def add_line_numbers(code):
    """Adds line numbers to code."""
    code = code.split("\n")
    return "\n".join([f"{idx} {line}" for idx, line in enumerate(code)])


def is_json_serializable(obj):
    """Check if an object is JSON serializable"""
    try:
        json.dumps(obj)
        return True
    except (TypeError, OverflowError):
        return False


def setup_colored_logging():
    """Setup colored logging with different colors for different log levels."""
    
    # Create a custom formatter with colors
    formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )
    
    # Create console handler with colored output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Create file handler with plain text (no colors for file)
    file_handler = logging.FileHandler('app.log')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)