import asyncio
import sys

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError

from config import BOT_PROXY, BOT_TOKEN


def create_bot() -> Bot:
    session = AiohttpSession(proxy=BOT_PROXY) if BOT_PROXY else AiohttpSession()
    return Bot(
        token=BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


async def check_telegram_api() -> tuple[bool, str]:
  if not BOT_TOKEN:
    return False, "BOT_TOKEN не задан в .env"

  bot = create_bot()
  try:
    me = await bot.get_me()
    return True, f"Связь есть. Бот: @{me.username}"
  except TelegramNetworkError as exc:
    hint = (
      "\n\nНе удаётся подключиться к api.telegram.org.\n"
      "Что сделать:\n"
      "1) Включи VPN на компьютере\n"
      "2) Или укажи прокси в .env: BOT_PROXY=socks5://127.0.0.1:10808\n"
      "   (порт смотри в настройках VPN — Clash, v2rayN, Hiddify и т.д.)\n"
      "3) Запусти ПРОВЕРКА-СЕТИ.bat и пришли результат наставнику"
    )
    return False, f"{exc}{hint}"
  finally:
    await bot.session.close()


def main() -> None:
  ok, message = asyncio.run(check_telegram_api())
  print(message)
  sys.exit(0 if ok else 1)


if __name__ == "__main__":
  main()
