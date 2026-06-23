# VibeCoding Наставник — Telegram-бот

Бот-курс по вайбкодингу: 20 уроков, прогресс, оплата PRO через Telegram Stars.

## Быстрый старт

### 1. Создай бота

1. Открой [@BotFather](https://t.me/BotFather)
2. `/newbot` → имя и username
3. Скопируй **токен**

### 2. Настрой окружение

```bash
cd "cursor practice/vibecoding-bot"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

В `.env` вставь:
- `BOT_TOKEN` — токен от BotFather
- `ADMIN_IDS` — твой Telegram ID (узнать: @userinfobot)

### 3. Запуск

```bash
python bot.py
```

Открой бота в Telegram → `/start`

## Структура

- `content/lessons.json` — все уроки (редактируй текст здесь)
- `handlers/` — логика бота
- `database/db.py` — SQLite (прогресс, оплаты)
- `keyboards/` — кнопки

## PRO и Stars

В @BotFather для бота включи **Payments** (если доступно в регионе).
Цена в `.env`: `PRO_PRICE_STARS=200`

## Деплой на Bothost.ru

1. Загрузи проект на **GitHub** (без `.env`, `.venv`, `*.db`)
2. [bothost.ru/create-bot.php](https://bothost.ru/create-bot.php) → Telegram, aiogram, `bot.py`
3. Переменные окружения — см. `bothost.env.example`
4. Deploy → в логах `Run polling for bot @...`

Подробная инструкция: **`BOTHOST-ДЕПЛОЙ.txt`**

База SQLite хранится в `/app/data` на сервере (папка `data/` локально).


## Команды

- `/start` — главное меню
- `/help` — помощь
- `/stats` — статистика (только admin)
