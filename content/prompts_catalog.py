import json
from dataclasses import dataclass
from html import escape
from pathlib import Path

from config import CONTENT_DIR


@dataclass(frozen=True)
class CursorPrompt:
    id: str
    title: str
    goal: str
    prompt: str
    tips: list[str]


class PromptsCatalog:
    def __init__(self, path: Path | None = None) -> None:
        self._path = path or CONTENT_DIR / "prompts.json"
        self._prompts: dict[str, CursorPrompt] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.is_file():
            return
        data = json.loads(self._path.read_text(encoding="utf-8"))
        for item in data.get("prompts", []):
            prompt = CursorPrompt(
                id=item["id"],
                title=item["title"],
                goal=item["goal"],
                prompt=item["prompt"],
                tips=item.get("tips", []),
            )
            self._prompts[prompt.id] = prompt

    @property
    def prompts(self) -> list[CursorPrompt]:
        return list(self._prompts.values())

    def get_prompt(self, prompt_id: str) -> CursorPrompt | None:
        return self._prompts.get(prompt_id)

    def format_preview(self, prompt: CursorPrompt) -> str:
        return (
            f"<b>{prompt.title}</b>\n\n"
            f"<b>Что получится:</b>\n{prompt.goal}"
        )

    def format_full(self, prompt: CursorPrompt) -> str:
        tips = "\n".join(f"• {tip}" for tip in prompt.tips)
        return (
            f"<b>{prompt.title}</b>\n\n"
            f"<b>Что получится:</b>\n{prompt.goal}\n\n"
            f"<b>Промпт для Cursor</b> (зажми и скопируй):\n"
            f"<pre>{escape(prompt.prompt)}</pre>\n\n"
            f"<b>Советы:</b>\n{tips}"
        )
