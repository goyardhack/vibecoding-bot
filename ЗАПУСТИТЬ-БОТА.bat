@echo off
cd /d "%~dp0"
call .venv\Scripts\activate
echo Запускаю VibeCoding бота...
python bot.py
pause
