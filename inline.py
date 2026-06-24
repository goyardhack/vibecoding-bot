from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from content.catalog import Lesson, LessonCatalog, Module


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="▶️ Продолжить обучение")],
            [KeyboardButton(text="📚 Обучение")],
            [
                KeyboardButton(text="🎯 Промпты Cursor"),
                KeyboardButton(text="🛠 Ошибки новичков"),
            ],
            [
                KeyboardButton(text="📊 Мой прогресс"),
                KeyboardButton(text="📅 Задание дня"),
            ],
            [KeyboardButton(text="⭐ PRO доступ"), KeyboardButton(text="❓ Помощь")],
        ],
        resize_keyboard=True,
    )


def modules_keyboard(catalog: LessonCatalog) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=module.title, callback_data=f"module:{module.id}")]
        for module in catalog.modules
    ]
    rows.append([InlineKeyboardButton(text="🏠 В меню", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def lessons_keyboard(
    module: Module,
    completed: set[int],
    has_pro: bool,
    purchased: set[int],
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []

    for lesson in module.lessons:
        icon = "✅" if lesson.id in completed else "📘"
        if lesson.access == "pro" and not has_pro:
            icon = "🔓" if lesson.id in purchased else "🔒"
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{icon} {lesson.id}. {lesson.title}",
                    callback_data=f"lesson:{lesson.id}",
                )
            ]
        )

    rows.append([InlineKeyboardButton(text="⬅️ К модулям", callback_data="modules")])
    rows.append([InlineKeyboardButton(text="🏠 В меню", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def lesson_actions_keyboard(
    lesson: Lesson,
    next_lesson: Lesson | None,
    has_pro: bool,
    purchased: set[int],
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text="✅ Отметить пройденным",
                callback_data=f"done:{lesson.id}",
            )
        ]
    ]

    if next_lesson:
        next_locked = (
            next_lesson.access == "pro"
            and not has_pro
            and next_lesson.id not in purchased
        )
        if next_locked:
            rows.append(
                [
                    InlineKeyboardButton(
                        text="🔒 Следующий урок (PRO)",
                        callback_data=f"lesson:{next_lesson.id}",
                    )
                ]
            )
        else:
            rows.append(
                [
                    InlineKeyboardButton(
                        text="➡️ Следующий урок",
                        callback_data=f"lesson:{next_lesson.id}",
                    )
                ]
            )

    rows.append(
        [
            InlineKeyboardButton(
                text="⬅️ К модулю",
                callback_data=f"module:{lesson.module_id}",
            )
        ]
    )
    rows.append([InlineKeyboardButton(text="🏠 В меню", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def pro_locked_keyboard(
    pro_price: int, lesson_price: int, lesson_id: int
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"⭐ PRO — все уроки ({pro_price} Stars)",
                    callback_data="buy_pro",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"📘 Только этот урок ({lesson_price} Stars)",
                    callback_data=f"buy_lesson:{lesson_id}",
                )
            ],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="modules")],
        ]
    )


def pro_offer_keyboard(pro_price: int, lesson_price: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"⭐ PRO — все уроки ({pro_price} Stars)",
                    callback_data="buy_pro",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"📘 Один урок ({lesson_price} Stars)",
                    callback_data="buy_lesson_menu",
                )
            ],
            [InlineKeyboardButton(text="🏠 В меню", callback_data="menu")],
        ]
    )
