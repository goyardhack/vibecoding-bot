import json
from dataclasses import dataclass
from pathlib import Path

from config import CONTENT_DIR


@dataclass(frozen=True)
class Lesson:
    id: int
    module_id: str
    module_title: str
    title: str
    access: str
    body: str
    practice: str
    key_points: list[str]


@dataclass(frozen=True)
class Module:
    id: str
    title: str
    lessons: list[Lesson]


class LessonCatalog:
    def __init__(self, path: Path | None = None) -> None:
        self._path = path or CONTENT_DIR / "lessons.json"
        self._modules: list[Module] = []
        self._lessons_by_id: dict[int, Lesson] = {}
        self._load()

    def _load(self) -> None:
        data = json.loads(self._path.read_text(encoding="utf-8"))
        modules: list[Module] = []

        for module_data in data["modules"]:
            lessons: list[Lesson] = []
            for lesson_data in module_data["lessons"]:
                lesson = Lesson(
                    id=lesson_data["id"],
                    module_id=module_data["id"],
                    module_title=module_data["title"],
                    title=lesson_data["title"],
                    access=lesson_data.get("access", "free"),
                    body=lesson_data["body"],
                    practice=lesson_data["practice"],
                    key_points=lesson_data.get("key_points", []),
                )
                lessons.append(lesson)
                self._lessons_by_id[lesson.id] = lesson

            modules.append(
                Module(
                    id=module_data["id"],
                    title=module_data["title"],
                    lessons=lessons,
                )
            )

        self._modules = modules

    @property
    def modules(self) -> list[Module]:
        return self._modules

    @property
    def total_lessons(self) -> int:
        return len(self._lessons_by_id)

    def get_lesson(self, lesson_id: int) -> Lesson | None:
        return self._lessons_by_id.get(lesson_id)

    def get_next_lesson(self, lesson_id: int) -> Lesson | None:
        lesson = self.get_lesson(lesson_id)
        if not lesson:
            return None

        for module in self._modules:
            ids = [item.id for item in module.lessons]
            if lesson_id in ids:
                index = ids.index(lesson_id)
                if index + 1 < len(ids):
                    return module.lessons[index + 1]
                module_index = self._modules.index(module)
                if module_index + 1 < len(self._modules):
                    return self._modules[module_index + 1].lessons[0]
                return None
        return None

    def get_module(self, module_id: str) -> Module | None:
        for module in self._modules:
            if module.id == module_id:
                return module
        return None

    def get_continue_lesson(
        self,
        completed: set[int],
        has_pro: bool,
        purchased: set[int],
    ) -> Lesson | None:
        for lesson_id in sorted(self._lessons_by_id):
            if lesson_id in completed:
                continue
            lesson = self._lessons_by_id[lesson_id]
            if lesson.access != "pro" or has_pro or lesson_id in purchased:
                return lesson
        return None
