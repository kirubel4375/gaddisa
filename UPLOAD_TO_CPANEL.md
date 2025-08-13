# Files to Upload to cPanel

After implementing language support, the following files need to be uploaded to your cPanel server:

## Core Language Files:

1. `emergency_bot/utils/translations.py` - Contains the translation dictionaries and utility functions
2. `emergency_bot/utils/__init__.py` - Package marker file

## Bot Integration Files:

3. `emergency_bot/telegram_bot/language_bridge.py` - Connects the language system with the bot
4. `emergency_bot/telegram_bot/bot.py` - Updated bot file with language support
5. `run_cpanel_bot.py` - Updated script to run the bot on cPanel
6. `bot_runner.py` - Script to run the bot in a separate process

## Translation Files:

7. `locale/en/LC_MESSAGES/django.po` - English translations
8. `locale/am/LC_MESSAGES/django.po` - Amharic translations
9. `locale/om/LC_MESSAGES/django.po` - Afaan Oromo translations

## Configuration:

10. `emergency_bot/settings.py` - Updated Django settings with internationalization support

## Documentation:

11. `LANGUAGE_SUPPORT.md` - Documentation on the language functionality

## Upload Instructions:

1. Upload the files in the same directory structure as your local development environment
2. Make sure all Python files have execution permissions (chmod +x)
3. Stop the existing bot process if it's running:
   ```bash
   kill $(cat bot.pid)
   ```
4. Start the new bot:
   ```bash
   python run_cpanel_bot.py
   ```
5. Check the logs for any errors:
   ```bash
   tail -f bot_output.log
   tail -f bot_error.log
   ```

## Troubleshooting:

If the bot doesn't work after uploading:

1. Check the log files for errors
2. Make sure the directory structure is correct
3. Verify that the PYTHONPATH includes all necessary directories
4. Restart the bot process manually using the commands above
5. Verify that all required Python packages are installed (check requirements.txt) 