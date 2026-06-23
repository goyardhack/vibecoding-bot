from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from config import SUPPORT_USERNAME
from content.catalog import LessonCatalog
from database.db import ensure_user
from keyboards.inline import main_menu_keyboard

router = Router()
catalog = LessonCatalog()

WELCOME_TEXT = (
    "Привет! Я <b>VibeCoding Наставник</b> — бот, который учит вайбкодингу "
    "так же, как личный наставник в Cursor.\n\n"
    "Формат: <b>Практика → Результат → Объяснение → Закрепление</b>\n\n"
    "Нажми <b>📚 Обучение</b>, выбери модуль и урок. "
    "Бесплатно — 10 уроков, PRO — ещё 10 с оплатой через Telegram Stars.\n\n"
    f"Всего уроков: <b>{catalog.total_lessons}</b>"
)

HELP_TEXT = (
    "<b>Как пользоваться</b>\n\n"
    "📚 <b>Обучение</b> — модули и уроки\n"
    "📊 <b>Мой прогресс</b> — сколько уроков пройдено\n"
    "⭐ <b>PRO доступ</b> — платные уроки и оплата Stars\n"
    "❓ <b>Помощь</b> — эта инструкция\n\n"
    "<b>Совет:</b> проходи уроки по порядку и делай задание из блока "
    "«Практика» — так быстрее научишься.\n\n"
    f"Вопросы: напиши @{SUPPORT_USERNAME}"
)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await ensure_user(message.from_user.id, message.from_user.username)
    await message.answer(WELCOME_TEXT, reply_markup=main_menu_keyboard())


@router.message(Command("help"))
@router.message(lambda m: m.text == "❓ Помощь")
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, reply_markup=main_menu_keyboard())


@router.message(lambda m: m.text == "🏠 В меню")
async def back_to_menu(message: Message) -> None:
    await message.answer("Главное меню 👇", reply_markup=main_menu_keyboard())
