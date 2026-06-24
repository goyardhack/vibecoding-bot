import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from config import CONTENT_DIR, DAILY_PRACTICE_TIMEZONE

DIFFICULTY_LABELS = {
    "easy": "🟢 Лёгкая",
    "medium": "🟡 Средняя",
    "hard": "🔴 Сложная",
}


@dataclass(frozen=True)
class DailyPractice:
    day: int
    difficulty: str
    title: str
    task: str


class DailyPracticeCatalog:
    def __init__(self, path: Path | None = None) -> None:
        self._path = path or CONTENT_DIR / "daily_practice.json"
        self._days: dict[int, DailyPractice] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.is_file():
            return
        data = json.loads(self._path.read_text(encoding="utf-8"))
        for item in data.get("days", []):
            practice = DailyPractice(
                day=item["day"],
                difficulty=item["difficulty"],
                title=item["title"],
                task=item["task"],
            )
            self._days[practice.day] = practice

    @property
    def total_days(self) -> int:
        return len(self._days)

    def get_practice(self, day: int) -> DailyPractice | None:
        return self._days.get(day)

    def get_day_index(self, when: datetime | date | None = None) -> int:
        if when is None:
            when = datetime.now(ZoneInfo(DAILY_PRACTICE_TIMEZONE))
        if isinstance(when, datetime):
            when = when.date()
        day_of_year = when.timetuple().tm_yday
        return (day_of_year - 1) % 365 + 1

    def get_today_practice(self, when: datetime | date | None = None) -> DailyPractice | None:
        return self.get_practice(self.get_day_index(when))

    def format_practice_message(
        self, practice: DailyPractice, *, as_notification: bool = False
    ) -> str:
        difficulty = DIFFICULTY_LABELS.get(practice.difficulty, practice.difficulty)
        header = "📅 <b>Задание дня</b>"
        if as_notification:
            header = "☀️ <b>Доброе утро! Задание дня</b>"

        return (
            f"{header}\n"
            f"День <b>{practice.day}</b> из <b>{self.total_days}</b>\n"
            f"{difficulty}\n\n"
            f"<b>{practice.title}</b>\n\n"
            f"{practice.task}"
        )
