@echo off
echo Starting Emergency Bot System with comprehensive setup...

echo 1. Starting Django server in background...
start /b python manage.py runserver

echo 2. Starting ngrok tunnel...
start /b ngrok http 8000

echo 3. Waiting for ngrok to initialize (10 seconds)...
timeout /t 10 /nobreak > nul

echo 4. Updating ngrok webhook...
python update_ngrok_url.py

echo 5. Starting Telegram bot...
python emergency_bot/scripts/run_bot.py

echo Emergency Bot System setup complete!
echo Press Ctrl+C to exit. 