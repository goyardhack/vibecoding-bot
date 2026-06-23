import asyncio
import logging
import sys

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError, TelegramUnauthorizedError

from config import BOT_PROXY, BOT_TOKEN, IS_BOTHOST

logger = logging.getLogger(__name__)


def create_bot() -> Bot:
    session = AiohttpSession(proxy=BOT_PROXY) if BOT_PROXY else AiohttpSession()
    return Bot(
        token=BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


async def check_telegram_api(retries: int = 3) -> tuple[bool, str]:
    if not BOT_TOKEN:
        return False, (
            "Токен не задан. В Bothost → {} добавь VIBECODING_TOKEN=токен от @BotFather"
        )

    bot = create_bot()
    last_error = "неизвестная ошибка"

    try:
        for attempt in range(1, retries + 1):
            try:
                me = await bot.get_me()
                return True, f"Связь есть. Бот: @{me.username}"
            except TelegramUnauthorizedError:
                return False, "Неверный BOT_TOKEN. Проверь токен в @BotFather и в панели Bothost."
            except TelegramNetworkError as exc:
                last_error = str(exc)
                if attempt < retries:
                    await asyncio.sleep(2)
        hint = (
            "\n\nНе удаётся подключиться к api.telegram.org.\n"
            "На Bothost обычно не нужен VPN. Проверь токен и логи.\n"
            "Локально: включи VPN или BOT_PROXY в .env."
        )
        return False, f"{last_error}{hint}"
    finally:
        await bot.session.close()
