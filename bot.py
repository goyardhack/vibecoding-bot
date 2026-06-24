import asyncio
import logging
import sys

from aiogram import Dispatcher
from aiogram.exceptions import TelegramNetworkError

from check_network import check_telegram_api, create_bot
from config import IS_BOTHOST
from database.db import init_db
from handlers import admin, daily, faq, lessons, payment, prompts, start
from services.bot_commands import setup_bot_commands
from services.daily_scheduler import run_daily_practice_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def main() -> None:
    logger.info("Запуск VibeCoding бота (bothost=%s)", IS_BOTHOST)

    ok, message = await check_telegram_api(retries=5 if IS_BOTHOST else 3)
    if not ok:
        logger.error(message)
        raise SystemExit(1)

    logger.info(message)
    await init_db()

    bot = create_bot()
    await setup_bot_commands(bot)
    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(lessons.router)
    dp.include_router(daily.router)
    dp.include_router(prompts.router)
    dp.include_router(faq.router)
    dp.include_router(payment.router)
    dp.include_router(admin.router)

    asyncio.create_task(run_daily_practice_scheduler(bot))

    try:
        logger.info("Старт polling...")
        await dp.start_polling(bot)
    except TelegramNetworkError as exc:
        logger.error("Сеть оборвалась: %s", exc)
        raise SystemExit(1) from exc
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
