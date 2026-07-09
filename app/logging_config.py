import logging
import os
from pathlib import Path


LOGGER_NAME = "ai_receptionist"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOG_FILE = Path("logs") / "app.log"


def get_log_file_path() -> Path:
    configured_path = os.getenv("LOG_FILE_PATH")
    if configured_path:
        return Path(configured_path)
    logger = logging.getLogger(LOGGER_NAME)
    active_path = getattr(logger, "_assignment4_log_file", None)
    if active_path:
        return Path(active_path)
    return Path(os.getenv("LOG_FILE_PATH", str(DEFAULT_LOG_FILE)))


def configure_application_logging() -> logging.Logger:
    log_file = get_log_file_path()
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter(LOG_FORMAT)

    for handler in list(logger.handlers):
        if getattr(handler, "_assignment4_handler", False):
            logger.removeHandler(handler)
            handler.close()

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    file_handler._assignment4_handler = True

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    stream_handler._assignment4_handler = True

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger._assignment4_log_file = str(log_file)
    return logger


def read_recent_log_lines(limit: int = 50) -> list[str]:
    log_file = get_log_file_path()
    if not log_file.exists():
        return []

    lines = log_file.read_text(encoding="utf-8").splitlines()
    return lines[-limit:]
