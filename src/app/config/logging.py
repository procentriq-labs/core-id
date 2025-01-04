import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .loader import load_settings

settings = load_settings()

LOG_LEVELS = {
    "development": logging.DEBUG,
    "production": logging.INFO,
    "default": logging.WARNING,
}

def configure_logging():
    """Configure logging based on environment and settings."""
    log_level = LOG_LEVELS.get(settings.environment, logging.WARNING)

    logs_dir = Path(__file__).parent.parent.parent / settings.logging.logfile_path
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Define the full path for the log file
    log_file_path = logs_dir / settings.logging.logfile_name

    # Basic logging configuration
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s | %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),  # Logs to stderr (console)
            RotatingFileHandler(
                filename=log_file_path,
                maxBytes=settings.logging.logfile_max_size_bytes,
                backupCount=settings.logging.logfile_max_count,
            )
        ]
    )

    # Adjust Uvicorn and FastAPI loggers
    uvicorn_loggers = [
        logging.getLogger("uvicorn"),
        logging.getLogger("uvicorn.error"),
        logging.getLogger("uvicorn.access"),
    ]

    for logger in uvicorn_loggers:
        logger.handlers.clear()
        logger.setLevel(log_level)
        for handler in logging.getLogger().handlers:
            logger.addHandler(handler)

    # Supress non-relevant Passlib logs to avoid Error about wrong passlib version (bug in Passlib)
    logging.getLogger('passlib').setLevel(logging.ERROR)
