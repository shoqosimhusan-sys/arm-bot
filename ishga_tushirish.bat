@echo off
chcp 65001 > nul
title ARM Kutubxona Telegram Boti
echo ========================================================
echo   Axborot-Resurs Markazi (ARM) Telegram Boti
echo ========================================================
echo.

set PYTHON_PATH="%LOCALAPPDATA%\Programs\Python\Python312\python.exe"

if exist %PYTHON_PATH% (
    echo Bot ishga tushirilmoqda...
    %PYTHON_PATH% bot.py
) else (
    where python >nul 2>nul
    if %errorlevel% equ 0 (
        python bot.py
    ) else (
        echo [XATOLIK] Python topilmadi!
        pause
    )
)
pause
