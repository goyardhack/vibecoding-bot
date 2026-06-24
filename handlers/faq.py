import json
from pathlib import Path

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import CONTENT_DIR
from keyboards.inline import main_menu_keyboard

router = Router()

_faq_items: list[dict] | None = None
_faq_by_id: dict[str, dict] | None = None


def _load_faq() -> None:
    global _faq_items, _faq_by_id
    if _faq_items is not None:
        return
    path = CONTENT_DIR / "faq.json"
    if not path.is_file():
        _faq_items = []
        _faq_by_id = {}
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    _faq_items = data.get("items", [])
    _faq_by_id = {item["id"]: item for item in _faq_items}


def get_faq_items() -> list[dict]:
    _load_faq()
    return _faq_items or []


def get_faq_item(item_id: str) -> dict | None:
    _load_faq()
    return (_faq_by_id or {}).get(item_id)


def faq_list_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text=item["question"],
                callback_data=f"faq:open:{item['id']}",
            )
        ]
        for item in get_faq_items()
    ]
    rows.append([InlineKeyboardButton(text="🏠 В меню", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def faq_answer_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ К списку", callback_data="faq:list")],
            [InlineKeyboardButton(text="🏠 В меню", callback_data="menu")],
        ]
    )


FAQ_INTRO = (
    "<b>🛠 Ошибки новичков</b>\n\n"
    "Выбери проблему — откроется пошаговое решение:"
)


async def show_faq_list(message: Message) -> None:
    if not get_faq_items():
        await message.answer(
            "Раздел временно недоступен. Напиши в поддержку.",
            reply_markup=main_menu_keyboard(),
        )
        return
    await message.answer(FAQ_INTRO, reply_markup=faq_list_keyboard())


@router.message(F.text == "🛠 Ошибки новичков")
@router.message(Command("faq"))
async def cmd_faq(message: Message) -> None:
    await show_faq_list(message)


@router.callback_query(F.data == "faq:list")
async def callback_faq_list(callback: CallbackQuery) -> None:
    await callback.message.edit_text(FAQ_INTRO, reply_markup=faq_list_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("faq:open:"))
async def callback_faq_open(callback: CallbackQuery) -> None:
    item_id = callback.data.split(":", 2)[2]
    item = get_faq_item(item_id)
    if not item:
        await callback.answer("Вопрос не найден", show_alert=True)
        return

    text = (
        f"<b>{item['question']}</b>\n\n"
        f"<blockquote>{item['answer']}</blockquote>"
    )
    await callback.message.edit_text(text, reply_markup=faq_answer_keyboard())
    await callback.answer()
