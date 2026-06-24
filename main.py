"""Точка входа для Bothost (ищет main.py или bot.py)."""
import asyncio

from bot import main

if __name__ == "__main__":
    asyncio.run(main())
