from aiogram import Bot
from aiogram.types import BotCommand, MenuButtonCommands


async def setup_bot_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="resume", description="Продолжить обучение"),
        BotCommand(command="learn", description="Обучение — модули"),
        BotCommand(command="progress", description="Мой прогресс"),
        BotCommand(command="daily", description="Задание дня"),
        BotCommand(command="prompts", description="Промпты Cursor"),
        BotCommand(command="faq", description="Ошибки новичков"),
        BotCommand(command="pro", description="PRO доступ"),
        BotCommand(command="help", description="Помощь"),
    ]
    await bot.set_my_commands(commands)
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())
