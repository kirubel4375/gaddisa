@echo off
echo ========================================================
echo EMERGENCY BOT SYSTEM - USING DIRECT IP CONNECTION
echo ========================================================

echo 1. Checking your public IP address...
curl -s https://api.ipify.org > public_ip.txt
set /p PUBLIC_IP=<public_ip.txt
echo Your public IP is: %PUBLIC_IP%

echo 2. Stopping any existing processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Django*" 2>nul
taskkill /F /IM ngrok.exe 2>nul
timeout /t 2 /nobreak > nul

echo 3. Setting up webapp URL with your public IP...
echo https://%PUBLIC_IP%:8000 > ngrok_url.txt
echo WebApp URL set to: https://%PUBLIC_IP%:8000

echo 4. Starting Django server on all interfaces...
start /b cmd /c "python manage.py runserver 0.0.0.0:8000"

echo 5. Waiting for Django to initialize (5 seconds)...
timeout /t 5 /nobreak > nul

echo 6. Updating webhook URL...
python update_ngrok_url.py

echo 7. Starting Telegram bot...
python emergency_bot/scripts/run_bot.py

echo ========================================================
echo NOTE: For this method to work, you need to:
echo 1. Configure your router to forward port 8000 to this computer
echo 2. Ensure your ISP doesn't block incoming connections
echo 3. You may need to set up HTTPS with a certificate
echo ======================================================== 