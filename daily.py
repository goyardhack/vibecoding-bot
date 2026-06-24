from aiogram import F, Router
from aiogram.types import Message

from aiogram.filters import Command

from content.daily_catalog import DailyPracticeCatalog
from keyboards.inline import main_menu_keyboard

router = Router()
catalog = DailyPracticeCatalog()


@router.message(F.text == "📅 Задание дня")
@router.message(Command("daily"))
async def show_daily_practice(message: Message) -> None:
    practice = catalog.get_today_practice()
    if not practice:
        await message.answer(
            "Задание дня временно недоступно. Попробуй позже.",
            reply_markup=main_menu_keyboard(),
        )
        return

    await message.answer(
        catalog.format_practice_message(practice),
        reply_markup=main_menu_keyboard(),
    )
