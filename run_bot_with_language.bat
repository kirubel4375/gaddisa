@echo off
REM Run the Telegram bot with language support
echo Starting Telegram bot with language support...

REM Activate the virtual environment if it exists
IF EXIST venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) ELSE (
    echo No virtual environment found. Make sure to install dependencies manually.
)

REM Run the bot
python bot/telegram_bot.py

echo Bot stopped. Press any key to exit...
pause > nul 