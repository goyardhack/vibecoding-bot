@echo off
chcp 65001 >nul
start "" notepad "%~dp0BOTHOST-ДЕПЛОЙ.txt"
echo.
echo Открыл BOTHOST-ДЕПЛОЙ.txt — следуй шагам.
echo.
echo Кратко:
echo 1. Загрузи папку на GitHub (без .env и .venv)
echo 2. bothost.ru/create-bot.php
echo 3. Переменные из bothost.env.example
echo.
pause
