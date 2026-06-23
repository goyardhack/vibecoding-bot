import aiosqlite

from config import DB_PATH


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT,
                has_pro INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS progress (
                telegram_id INTEGER NOT NULL,
                lesson_id INTEGER NOT NULL,
                completed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (telegram_id, lesson_id)
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                stars_amount INTEGER NOT NULL,
                payment_id TEXT NOT NULL UNIQUE,
                purchase_type TEXT NOT NULL DEFAULT 'pro',
                lesson_id INTEGER,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS lesson_purchases (
                telegram_id INTEGER NOT NULL,
                lesson_id INTEGER NOT NULL,
                payment_id TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (telegram_id, lesson_id)
            )
            """
        )
        await db.commit()


async def ensure_user(telegram_id: int, username: str | None) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO users (telegram_id, username)
            VALUES (?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET username = excluded.username
            """,
            (telegram_id, username),
        )
        await db.commit()


async def user_has_pro(telegram_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT has_pro FROM users WHERE telegram_id = ?",
            (telegram_id,),
        )
        row = await cursor.fetchone()
        return bool(row and row[0])


async def grant_pro(telegram_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET has_pro = 1 WHERE telegram_id = ?",
            (telegram_id,),
        )
        await db.commit()


async def get_purchased_lessons(telegram_id: int) -> set[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT lesson_id FROM lesson_purchases WHERE telegram_id = ?",
            (telegram_id,),
        )
        rows = await cursor.fetchall()
        return {row[0] for row in rows}


async def user_has_lesson_access(
    telegram_id: int, lesson_id: int, access: str
) -> bool:
    if access != "pro":
        return True
    if await user_has_pro(telegram_id):
        return True
    purchased = await get_purchased_lessons(telegram_id)
    return lesson_id in purchased


async def grant_lesson_purchase(
    telegram_id: int, lesson_id: int, payment_id: str
) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO lesson_purchases (telegram_id, lesson_id, payment_id)
            VALUES (?, ?, ?)
            """,
            (telegram_id, lesson_id, payment_id),
        )
        await db.commit()


async def mark_lesson_completed(telegram_id: int, lesson_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO progress (telegram_id, lesson_id)
            VALUES (?, ?)
            """,
            (telegram_id, lesson_id),
        )
        await db.commit()


async def get_completed_lessons(telegram_id: int) -> set[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT lesson_id FROM progress WHERE telegram_id = ?",
            (telegram_id,),
        )
        rows = await cursor.fetchall()
        return {row[0] for row in rows}


async def save_purchase(
    telegram_id: int,
    stars_amount: int,
    payment_id: str,
    purchase_type: str = "pro",
    lesson_id: int | None = None,
) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO purchases (
                telegram_id, stars_amount, payment_id, purchase_type, lesson_id
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (telegram_id, stars_amount, payment_id, purchase_type, lesson_id),
        )
        await db.commit()


async def get_stats() -> dict[str, int]:
    async with aiosqlite.connect(DB_PATH) as db:
        users = await (await db.execute("SELECT COUNT(*) FROM users")).fetchone()
        pro_users = await (
            await db.execute("SELECT COUNT(*) FROM users WHERE has_pro = 1")
        ).fetchone()
        completed = await (
            await db.execute("SELECT COUNT(*) FROM progress")
        ).fetchone()
        purchases = await (
            await db.execute("SELECT COUNT(*) FROM purchases")
        ).fetchone()
        return {
            "users": users[0] if users else 0,
            "pro_users": pro_users[0] if pro_users else 0,
            "completed_lessons": completed[0] if completed else 0,
            "purchases": purchases[0] if purchases else 0,
        }
