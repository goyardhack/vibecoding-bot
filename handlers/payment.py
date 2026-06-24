from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery

from config import (
    LESSON_PRICE_STARS,
    PRO_DESCRIPTION,
    PRO_PRICE_STARS,
    PRO_TITLE,
    PROMPTS_DESCRIPTION,
    PROMPTS_PRICE_STARS,
    PROMPTS_TITLE,
)
from content.catalog import LessonCatalog
from database.db import (
    grant_lesson_purchase,
    grant_pro,
    grant_prompts,
    save_purchase,
    user_has_pro,
    user_has_prompts_access,
)
from keyboards.inline import main_menu_keyboard, pro_offer_keyboard

router = Router()
catalog = LessonCatalog()

PRO_INFO = (
    "<b>⭐ PRO доступ</b>\n\n"
    "Что входит:\n"
    "• Все 10 платных уроков сразу\n"
    "• 6 готовых промптов для Cursor\n"
    "• Продвинутые темы: промпты, деплой, продажи, Python, API\n"
    "• Доступ навсегда после оплаты\n\n"
    f"Подписка: <b>{PRO_PRICE_STARS} Stars</b> — всё включено\n"
    f"Один урок: <b>{LESSON_PRICE_STARS} Stars</b> — только выбранный\n"
    f"Только промпты: <b>{PROMPTS_PRICE_STARS} Stars</b> — без уроков\n\n"
    "Оплата прямо в Telegram."
)


@router.message(F.text == "⭐ PRO доступ")
@router.message(Command("pro"))
async def show_pro(message: Message) -> None:
    has_pro = await user_has_pro(message.from_user.id)
    if has_pro:
        await message.answer(
            "У тебя уже есть ⭐ PRO доступ. Все уроки и промпты открыты!",
            reply_markup=main_menu_keyboard(),
        )
        return

    await message.answer(
        PRO_INFO,
        reply_markup=pro_offer_keyboard(PRO_PRICE_STARS, LESSON_PRICE_STARS),
    )


@router.callback_query(F.data == "buy_pro")
async def buy_pro(callback: CallbackQuery) -> None:
    has_pro = await user_has_pro(callback.from_user.id)
    if has_pro:
        await callback.answer("PRO уже активен", show_alert=True)
        return

    await callback.message.answer_invoice(
        title=PRO_TITLE,
        description=PRO_DESCRIPTION,
        payload="pro_access_full",
        currency="XTR",
        prices=[LabeledPrice(label="PRO доступ", amount=PRO_PRICE_STARS)],
        provider_token="",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("buy_lesson:"))
async def buy_lesson(callback: CallbackQuery) -> None:
    lesson_id = int(callback.data.split(":", 1)[1])
    lesson = catalog.get_lesson(lesson_id)
    if not lesson or lesson.access != "pro":
        await callback.answer("Урок не найден", show_alert=True)
        return

    has_pro = await user_has_pro(callback.from_user.id)
    if has_pro:
        await callback.answer("У тебя уже PRO — все уроки открыты", show_alert=True)
        return

    await callback.message.answer_invoice(
        title=f"Урок {lesson.id}: {lesson.title}",
        description=f"Доступ к одному PRO-уроку курса VibeCoding.",
        payload=f"lesson:{lesson_id}",
        currency="XTR",
        prices=[LabeledPrice(label="Один урок", amount=LESSON_PRICE_STARS)],
        provider_token="",
    )
    await callback.answer()


@router.callback_query(F.data == "buy_prompts")
async def buy_prompts(callback: CallbackQuery) -> None:
    if await user_has_prompts_access(callback.from_user.id):
        await callback.answer("Промпты уже доступны", show_alert=True)
        return

    await callback.message.answer_invoice(
        title=PROMPTS_TITLE,
        description=PROMPTS_DESCRIPTION,
        payload="prompts_access",
        currency="XTR",
        prices=[LabeledPrice(label="Промпты Cursor", amount=PROMPTS_PRICE_STARS)],
        provider_token="",
    )
    await callback.answer()


@router.callback_query(F.data == "buy_lesson_menu")
async def buy_lesson_menu(callback: CallbackQuery) -> None:
    has_pro = await user_has_pro(callback.from_user.id)
    if has_pro:
        await callback.answer("У тебя уже PRO", show_alert=True)
        return

    await callback.message.answer(
        "Выбери PRO-урок в 📚 Обучение — на заблокированном уроке "
        f"можно купить только его за {LESSON_PRICE_STARS} Stars "
        f"или всю подписку за {PRO_PRICE_STARS} Stars.",
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()


@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery) -> None:
    payload = query.invoice_payload
    if payload == "pro_access_full":
        await query.answer(ok=True)
        return

    if payload == "prompts_access":
        await query.answer(ok=True)
        return

    if payload.startswith("lesson:"):
        lesson_id = int(payload.split(":", 1)[1])
        lesson = catalog.get_lesson(lesson_id)
        if lesson and lesson.access == "pro":
            await query.answer(ok=True)
            return

    await query.answer(ok=False, error_message="Некорректный платёж")


@router.message(F.successful_payment)
async def successful_payment(message: Message) -> None:
    payment = message.successful_payment
    payload = payment.invoice_payload

    if payload == "pro_access_full":
        await save_purchase(
            telegram_id=message.from_user.id,
            stars_amount=payment.total_amount,
            payment_id=payment.telegram_payment_charge_id,
            purchase_type="pro",
        )
        await grant_pro(message.from_user.id)
        await message.answer(
            "🎉 <b>PRO доступ активирован!</b>\n\n"
            "Все платные уроки и промпты для Cursor открыты. "
            "Нажми 📚 Обучение или 🎯 Промпты Cursor.",
            reply_markup=main_menu_keyboard(),
        )
        return

    if payload == "prompts_access":
        await save_purchase(
            telegram_id=message.from_user.id,
            stars_amount=payment.total_amount,
            payment_id=payment.telegram_payment_charge_id,
            purchase_type="prompts",
        )
        await grant_prompts(message.from_user.id)
        await message.answer(
            "🎉 <b>Промпты для Cursor открыты!</b>\n\n"
            "Нажми 🎯 Промпты Cursor и выбери нужный.",
            reply_markup=main_menu_keyboard(),
        )
        return

    if payload.startswith("lesson:"):
        lesson_id = int(payload.split(":", 1)[1])
        lesson = catalog.get_lesson(lesson_id)
        if not lesson:
            await message.answer("Оплата прошла, но урок не найден. Напиши в поддержку.")
            return

        await save_purchase(
            telegram_id=message.from_user.id,
            stars_amount=payment.total_amount,
            payment_id=payment.telegram_payment_charge_id,
            purchase_type="lesson",
            lesson_id=lesson_id,
        )
        await grant_lesson_purchase(
            message.from_user.id,
            lesson_id,
            payment.telegram_payment_charge_id,
        )
        await message.answer(
            f"✅ <b>Урок {lesson.id} открыт!</b>\n\n"
            f"«{lesson.title}» — нажми 📚 Обучение и открой урок.",
            reply_markup=main_menu_keyboard(),
        )
        return

    await message.answer("Оплата получена. Если доступ не открылся — напиши в поддержку.")
