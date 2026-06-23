import asyncio
import logging
import sys

from aiogram import Dispatcher
from aiogram.exceptions import TelegramNetworkError

from check_network import check_telegram_api, create_bot
from database.db import init_db
from handlers import admin, lessons, payment, start

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


async def main() -> None:
    ok, message = await check_telegram_api()
    if not ok:
        print(message)
        raise SystemExit(1)

    logger.info(message)
    await init_db()

    bot = create_bot()
    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(lessons.router)
    dp.include_router(payment.router)
    dp.include_router(admin.router)

    try:
        await dp.start_polling(bot)
    except TelegramNetworkError as exc:
        print(
            f"\nСеть оборвалась: {exc}\n"
            "Включи VPN или пропиши BOT_PROXY в .env и перезапусти бота."
        )
        raise SystemExit(1) from exc
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
