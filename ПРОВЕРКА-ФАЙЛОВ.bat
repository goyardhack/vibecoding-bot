@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo === Проверка файлов для Bothost ===
echo.
.venv\Scripts\python.exe -c "from services.startup_check import check_required_files; m=check_required_files(); print('OK - все файлы на месте' if not m else 'ОШИБКА - не хватает:'); [print('  -',x) for x in m]"
echo.
pause
