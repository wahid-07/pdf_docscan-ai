import logging
from datetime import datetime
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("pdf_extractor.audit")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.FileHandler(LOG_DIR / "audit.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    logger.addHandler(handler)


def log_event(event: str, user_id: int | None = None, details: str | None = None):
    message = f"event={event} user_id={user_id if user_id is not None else 'system'}"
    if details:
        message += f" details={details}"
    logger.info(message)
