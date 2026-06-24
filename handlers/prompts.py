from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import PROMPTS_PRICE_STARS, PRO_PRICE_STARS
from content.prompts_catalog import PromptsCatalog
from database.db import user_has_prompts_access
from keyboards.inline import main_menu_keyboard

router = Router()
catalog = PromptsCatalog()

PROMPTS_INTRO = (
    "<b>🎯 Промпты для Cursor</b>\n\n"
    "6 готовых промптов — вставляешь в Cursor и получаешь рабочий результат.\n"
    "Каждый промпт: цель, полный текст запроса и советы.\n\n"
    "Выбери промпт:"
)

PROMPTS_LOCKED = (
    "<b>🎯 Промпты для Cursor</b>\n\n"
    "6 готовых промптов для лендинга, магазина, бота, портфолио и других проектов.\n\n"
    f"🔒 Доступ: <b>{PROMPTS_PRICE_STARS} Stars</b> — навсегда\n"
    f"⭐ Или в составе PRO ({PRO_PRICE_STARS} Stars) — уроки + промпты"
)


def prompts_list_keyboard(has_access: bool) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text=prompt.title,
                callback_data=f"prompt:{prompt.id}",
            )
        ]
        for prompt in catalog.prompts
    ]
    if not has_access:
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"🔓 Купить промпты ({PROMPTS_PRICE_STARS} Stars)",
                    callback_data="buy_prompts",
                )
            ]
        )
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"⭐ PRO — всё ({PRO_PRICE_STARS} Stars)",
                    callback_data="buy_pro",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text="🏠 В меню", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def prompt_back_keyboard(prompt_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ К списку промптов",
                    callback_data="prompts:list",
                )
            ],
            [InlineKeyboardButton(text="🏠 В меню", callback_data="menu")],
        ]
    )


async def show_prompts_menu(message: Message) -> None:
    if not catalog.prompts:
        await message.answer(
            "Промпты временно недоступны. Обновление на сервере — попробуй позже.",
            reply_markup=main_menu_keyboard(),
        )
        return
    has_access = await user_has_prompts_access(message.from_user.id)
    text = PROMPTS_INTRO if has_access else PROMPTS_LOCKED
    await message.answer(
        text,
        reply_markup=prompts_list_keyboard(has_access),
    )


@router.message(F.text == "🎯 Промпты Cursor")
@router.message(Command("prompts"))
async def cmd_prompts(message: Message) -> None:
    await show_prompts_menu(message)


@router.callback_query(F.data == "prompts:list")
async def callback_prompts_list(callback: CallbackQuery) -> None:
    has_access = await user_has_prompts_access(callback.from_user.id)
    text = PROMPTS_INTRO if has_access else PROMPTS_LOCKED
    await callback.message.edit_text(
        text,
        reply_markup=prompts_list_keyboard(has_access),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("prompt:"))
async def callback_prompt(callback: CallbackQuery) -> None:
    prompt_id = callback.data.split(":", 1)[1]
    if prompt_id == "list":
        return

    prompt = catalog.get_prompt(prompt_id)
    if not prompt:
        await callback.answer("Промпт не найден", show_alert=True)
        return

    has_access = await user_has_prompts_access(callback.from_user.id)
    if not has_access:
        await callback.message.edit_text(
            catalog.format_preview(prompt)
            + f"\n\n🔒 Полный промпт — после оплаты ({PROMPTS_PRICE_STARS} Stars)",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"🔓 Купить ({PROMPTS_PRICE_STARS} Stars)",
                            callback_data="buy_prompts",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="⬅️ Назад",
                            callback_data="prompts:list",
                        )
                    ],
                ]
            ),
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        catalog.format_full(prompt),
        reply_markup=prompt_back_keyboard(prompt_id),
    )
    await callback.answer()
