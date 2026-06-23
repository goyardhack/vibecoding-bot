from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards.main import main_menu_kb
from bot.states import ChatMode

router = Router()

WELCOME = (
    "👋 Привет! Я AI-бот на базе <b>Google Gemini</b>.\n\n"
    "Что умею:\n"
    "💬 <b>Общение</b> — отвечаю на любые вопросы\n"
    "📋 <b>План</b> — составляю пошаговые планы\n"
    "💡 <b>Советы</b> — даю взвешенные рекомендации\n"
    "🎨 <b>Картинка</b> — генерирую изображения за ⭐ Stars\n\n"
    "Выбери режим кнопкой ниже или просто напиши сообщение."
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(ChatMode.free)
    await message.answer(WELCOME, reply_markup=main_menu_kb())


@router.message(lambda m: m.text == "ℹ️ Помощь")
async def cmd_help(message: Message) -> None:
    await message.answer(
        "📖 <b>Как пользоваться:</b>\n\n"
        "• Нажми <b>💬 Общение</b>, <b>📋 План</b> или <b>💡 Советы</b> — и пиши запрос\n"
        "• <b>🎨 Картинка</b> — опиши что нарисовать, оплати Stars, получи результат\n"
        "• <b>🗑 Очистить историю</b> — сбросить контекст диалога\n\n"
        "AI: Google Gemini 2.0 Flash (текст) + Gemini Image (картинки)",
    )
