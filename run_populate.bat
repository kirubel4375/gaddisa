@echo off
echo Starting database population...
echo.

REM Try the Django management command first
echo Attempting to use Django management command...
python manage.py populate_db --clear
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Database populated successfully using Django management command!
    goto :end
)

echo.
echo Django management command failed, trying standalone script...
echo.

REM Try the standalone script
python populate_database.py --clear
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Database populated successfully using standalone script!
) else (
    echo.
    echo ❌ Both methods failed. Please check the error messages above.
    echo.
    echo Make sure you:
    echo 1. Are in the project root directory
    echo 2. Have activated your virtual environment
    echo 3. Have installed all required dependencies
    echo 4. Have run database migrations
)

:end
echo.
pause