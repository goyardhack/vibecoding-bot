from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from config import LESSON_PRICE_STARS, PRO_PRICE_STARS, SUPPORT_USERNAME
from content.catalog import Lesson, LessonCatalog
from database.db import (
    get_completed_lessons,
    get_purchased_lessons,
    mark_certificate_offered,
    mark_lesson_completed,
    user_has_lesson_access,
    user_has_pro,
    was_certificate_offered,
)
from keyboards.inline import (
    lesson_actions_keyboard,
    lessons_keyboard,
    main_menu_keyboard,
    modules_keyboard,
    pro_locked_keyboard,
)

router = Router()
catalog = LessonCatalog()


def format_lesson(lesson: Lesson, preview: bool = False) -> str:
    body = lesson.body
    if preview:
        body = body[:400].rstrip() + "…"

    points = "\n".join(f"• {point}" for point in lesson.key_points)
    text = (
        f"<b>{lesson.id}. {lesson.title}</b>\n"
        f"<i>{lesson.module_title}</i>\n\n"
        f"{body}\n\n"
    )

    if not preview:
        text += (
            f"<b>Практика</b>\n{lesson.practice}\n\n"
            f"<b>Важно понять</b>\n{points}"
        )
    else:
        text += (
            "\n🔒 <b>Это PRO-урок.</b> Ниже — превью.\n\n"
            f"⭐ Подписка PRO — <b>{PRO_PRICE_STARS} Stars</b> (все уроки)\n"
            f"📘 Только этот урок — <b>{LESSON_PRICE_STARS} Stars</b>"
        )

    return text


async def _lesson_reply(
    telegram_id: int, lesson_id: int
) -> tuple[str, InlineKeyboardMarkup] | None:
    lesson = catalog.get_lesson(lesson_id)
    if not lesson:
        return None

    has_pro = await user_has_pro(telegram_id)
    purchased = await get_purchased_lessons(telegram_id)
    has_access = await user_has_lesson_access(telegram_id, lesson_id, lesson.access)

    if lesson.access == "pro" and not has_access:
        return (
            format_lesson(lesson, preview=True),
            pro_locked_keyboard(PRO_PRICE_STARS, LESSON_PRICE_STARS, lesson_id),
        )

    next_lesson = catalog.get_next_lesson(lesson_id)
    return (
        format_lesson(lesson),
        lesson_actions_keyboard(lesson, next_lesson, has_pro, purchased),
    )


@router.message(F.text == "📚 Обучение")
@router.message(Command("learn"))
async def show_modules(message: Message) -> None:
    await message.answer(
        "Выбери модуль:",
        reply_markup=modules_keyboard(catalog),
    )


@router.message(F.text == "▶️ Продолжить обучение")
@router.message(Command("resume"))
@router.message(Command("continue"))
async def continue_learning(message: Message) -> None:
    completed = await get_completed_lessons(message.from_user.id)
    has_pro = await user_has_pro(message.from_user.id)
    purchased = await get_purchased_lessons(message.from_user.id)

    lesson = catalog.get_continue_lesson(completed, has_pro, purchased)
    if not lesson:
        await message.answer(
            "🎉 Все доступные уроки пройдены! Ты красава.\n\n"
            "Если хочешь открыть PRO-уроки — зайди в ⭐ PRO доступ.",
            reply_markup=main_menu_keyboard(),
        )
        return

    reply = await _lesson_reply(message.from_user.id, lesson.id)
    if not reply:
        await message.answer("Урок не найден", reply_markup=main_menu_keyboard())
        return

    text, keyboard = reply
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data == "modules")
async def callback_modules(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "Выбери модуль:",
        reply_markup=modules_keyboard(catalog),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("module:"))
async def callback_module(callback: CallbackQuery) -> None:
    module_id = callback.data.split(":", 1)[1]
    module = catalog.get_module(module_id)
    if not module:
        await callback.answer("Модуль не найден", show_alert=True)
        return

    completed = await get_completed_lessons(callback.from_user.id)
    has_pro = await user_has_pro(callback.from_user.id)
    purchased = await get_purchased_lessons(callback.from_user.id)

    await callback.message.edit_text(
        f"<b>{module.title}</b>\n\nВыбери урок:",
        reply_markup=lessons_keyboard(module, completed, has_pro, purchased),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("lesson:"))
async def callback_lesson(callback: CallbackQuery) -> None:
    lesson_id = int(callback.data.split(":", 1)[1])
    reply = await _lesson_reply(callback.from_user.id, lesson_id)
    if not reply:
        await callback.answer("Урок не найден", show_alert=True)
        return

    text, keyboard = reply
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("done:"))
async def callback_done(callback: CallbackQuery) -> None:
    lesson_id = int(callback.data.split(":", 1)[1])
    lesson = catalog.get_lesson(lesson_id)
    if not lesson:
        await callback.answer("Урок не найден", show_alert=True)
        return

    has_access = await user_has_lesson_access(
        callback.from_user.id, lesson_id, lesson.access
    )
    if not has_access:
        await callback.answer("Сначала открой доступ к уроку", show_alert=True)
        return

    await mark_lesson_completed(callback.from_user.id, lesson_id)
    await callback.answer("Урок отмечен как пройденный ✅")

    has_pro = await user_has_pro(callback.from_user.id)
    purchased = await get_purchased_lessons(callback.from_user.id)
    completed = await get_completed_lessons(callback.from_user.id)
    module = catalog.get_module(lesson.module_id)

    if module:
        await callback.message.edit_reply_markup(
            reply_markup=lessons_keyboard(module, completed, has_pro, purchased),
        )

    if (
        len(completed) >= catalog.total_lessons
        and not await was_certificate_offered(callback.from_user.id)
    ):
        await mark_certificate_offered(callback.from_user.id)
        await callback.message.answer(
            "🎉 <b>Поздравляем! Вы прошли VibeCode!</b>\n\n"
            f"Для получения сертификата напиши @{SUPPORT_USERNAME}"
        )


@router.callback_query(F.data == "menu")
async def callback_menu(callback: CallbackQuery) -> None:
    await callback.message.answer("Главное меню 👇", reply_markup=main_menu_keyboard())
    await callback.answer()


@router.message(F.text == "📊 Мой прогресс")
@router.message(Command("progress"))
async def show_progress(message: Message) -> None:
    completed = await get_completed_lessons(message.from_user.id)
    has_pro = await user_has_pro(message.from_user.id)
    purchased = await get_purchased_lessons(message.from_user.id)
    total = catalog.total_lessons
    done = len(completed)
    percent = round(done / total * 100) if total else 0

    last_lesson = max(completed) if completed else 0
    last_title = ""
    if last_lesson:
        lesson = catalog.get_lesson(last_lesson)
        last_title = lesson.title if lesson else ""

    if has_pro:
        status = "⭐ PRO — все уроки открыты"
    elif purchased:
        status = f"Куплено уроков: {len(purchased)} (без подписки)"
    else:
        status = "Бесплатный доступ (10 уроков)"

    text = (
        f"<b>Твой прогресс</b>\n\n"
        f"Пройдено: <b>{done}/{total}</b> уроков — <b>{percent}%</b>\n"
        f"Статус: {status}\n"
    )
    if last_title:
        text += f"Последний урок: <b>{last_lesson}. {last_title}</b>\n"

    if done == 0:
        text += "\nНажми ▶️ Продолжить обучение — начнёшь с урока 1."
    elif done < total:
        text += "\nПродолжай — нажми ▶️ Продолжить обучение."
    else:
        text += "\n🎉 Все уроки пройдены! Ты красава."

    await message.answer(text, reply_markup=main_menu_keyboard())
