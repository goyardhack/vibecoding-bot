import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
CONTENT_DIR = BASE_DIR / "content"
DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "bot.db"

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
# Прокси если api.telegram.org недоступен (VPN-клиенты часто дают socks5://127.0.0.1:10808)
BOT_PROXY = os.getenv("BOT_PROXY", "").strip()
ADMIN_IDS = {
    int(x.strip())
    for x in os.getenv("ADMIN_IDS", "").split(",")
    if x.strip().isdigit()
}

PRO_PRICE_STARS = int(os.getenv("PRO_PRICE_STARS", "450"))
LESSON_PRICE_STARS = int(os.getenv("LESSON_PRICE_STARS", "50"))
PRO_TITLE = os.getenv("PRO_TITLE", "PRO: Полный доступ к курсу")
PRO_DESCRIPTION = os.getenv(
    "PRO_DESCRIPTION",
    "10 платных уроков VibeCoding + обновления.",
)
