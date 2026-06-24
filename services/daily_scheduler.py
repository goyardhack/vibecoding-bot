import asyncio
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter

from config import DAILY_PRACTICE_HOUR, DAILY_PRACTICE_TIMEZONE
from content.daily_catalog import DailyPracticeCatalog
from database.db import get_all_user_ids, mark_daily_sent, was_daily_sent
from keyboards.inline import main_menu_keyboard

logger = logging.getLogger(__name__)
catalog = DailyPracticeCatalog()


async def send_daily_practice_to_user(
    bot: Bot, telegram_id: int, practice_day: int
) -> bool:
    if await was_daily_sent(telegram_id, practice_day):
        return False

    practice = catalog.get_practice(practice_day)
    if not practice:
        logger.warning("Задание дня %s не найдено", practice_day)
        return False

    text = catalog.format_practice_message(practice, as_notification=True)
    text += "\n\nНажми <b>📅 Задание дня</b> в меню, чтобы открыть снова."

    try:
        await bot.send_message(
            telegram_id,
            text,
            reply_markup=main_menu_keyboard(),
        )
    except TelegramForbiddenError:
        logger.info("Пользователь %s заблокировал бота", telegram_id)
        return False
    except TelegramRetryAfter as exc:
        await asyncio.sleep(exc.retry_after)
        await bot.send_message(
            telegram_id,
            text,
            reply_markup=main_menu_keyboard(),
        )
    except Exception:
        logger.exception("Не удалось отправить задание дня пользователю %s", telegram_id)
        return False

    await mark_daily_sent(telegram_id, practice_day)
    return True


async def broadcast_daily_practice(bot: Bot) -> None:
    practice_day = catalog.get_day_index()
    practice = catalog.get_practice(practice_day)
    if not practice:
        logger.error("Нет задания на день %s", practice_day)
        return

    user_ids = await get_all_user_ids()
    sent = 0
    for telegram_id in user_ids:
        if await send_daily_practice_to_user(bot, telegram_id, practice_day):
            sent += 1
        await asyncio.sleep(0.05)

    logger.info(
        "Ежедневная практика: день %s, отправлено %s из %s",
        practice_day,
        sent,
        len(user_ids),
    )


def _next_run_at(now: datetime) -> datetime:
    target = now.replace(
        hour=DAILY_PRACTICE_HOUR, minute=0, second=0, microsecond=0
    )
    if now >= target:
        target += timedelta(days=1)
    return target


async def run_daily_practice_scheduler(bot: Bot) -> None:
    tz = ZoneInfo(DAILY_PRACTICE_TIMEZONE)
    logger.info(
        "Планировщик заданий дня: %02d:00 %s",
        DAILY_PRACTICE_HOUR,
        DAILY_PRACTICE_TIMEZONE,
    )

    while True:
        now = datetime.now(tz)
        target = _next_run_at(now)

        if now.hour >= DAILY_PRACTICE_HOUR:
            await broadcast_daily_practice(bot)

        sleep_seconds = (target - datetime.now(tz)).total_seconds()
        if sleep_seconds > 0:
            logger.info("Следующая рассылка через %.0f сек", sleep_seconds)
            await asyncio.sleep(sleep_seconds)

        await broadcast_daily_practice(bot)
