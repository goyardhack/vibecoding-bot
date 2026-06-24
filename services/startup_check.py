import logging
from pathlib import Path

from config import CONTENT_DIR

logger = logging.getLogger(__name__)

REQUIRED_FILES = (
    "content/lessons.json",
    "content/prompts.json",
    "content/faq.json",
    "content/daily_practice.json",
    "handlers/start.py",
    "handlers/lessons.py",
    "handlers/prompts.py",
    "handlers/faq.py",
    "handlers/payment.py",
    "handlers/daily.py",
    "services/bot_commands.py",
    "services/daily_scheduler.py",
    "content/prompts_catalog.py",
    "content/daily_catalog.py",
)


def check_required_files(base_dir: Path | None = None) -> list[str]:
    root = base_dir or CONTENT_DIR.parent
    missing = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).is_file():
            missing.append(rel_path)
    return missing


def log_startup_status() -> bool:
    missing = check_required_files()
    if missing:
        logger.error("Не хватает файлов на сервере:")
        for path in missing:
            logger.error("  - %s", path)
        return False
    logger.info("Все обязательные файлы на месте")
    return True
