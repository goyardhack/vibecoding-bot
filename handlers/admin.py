from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import ADMIN_IDS
from database.db import get_stats

router = Router()


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    if message.from_user.id not in ADMIN_IDS:
        return

    stats = await get_stats()
    await message.answer(
        "<b>Статистика бота</b>\n\n"
        f"Пользователей: {stats['users']}\n"
        f"PRO: {stats['pro_users']}\n"
        f"Пройдено уроков (всего): {stats['completed_lessons']}\n"
        f"Покупок: {stats['purchases']}"
    )
