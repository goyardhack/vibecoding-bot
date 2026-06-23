@echo off
cd /d "%~dp0"
call .venv\Scripts\activate
pip install -r requirements.txt -q
echo === Проверка связи с Telegram ===
python check_network.py
echo.
pause
