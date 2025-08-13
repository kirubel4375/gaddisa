# Language Support in Telegram Emergency Bot

This document explains how the multilingual support works in the Telegram Emergency Bot.

## Supported Languages

The bot currently supports the following languages:

- English 🇬🇧 (en)
- Amharic 🇪🇹 (am)
- Afaan Oromo 🇪🇹 (om)

## How Language Selection Works

1. **Bot Buttons**: Users can change their language by clicking on the "Change Language 🌐" button or by typing `/language` command in the bot chat.

2. **User Preference Storage**: Language preferences are stored in the `UserProfile` model in the database.

3. **Translation Mechanism**: All text displayed to users is translated according to their language preference using a custom translation system.

## Translation System

The bot uses two translation mechanisms:

1. **Django's built-in translation system**: For Django templates and Python code.
2. **Custom translation dictionary**: For Telegram bot messages.

### Django Translation Files

Translation files are stored in the `locale` directory in the following structure:

```
locale/
  ├── en/
  │   └── LC_MESSAGES/
  │       └── django.po
  ├── am/
  │   └── LC_MESSAGES/
  │       └── django.po
  └── om/
      └── LC_MESSAGES/
          └── django.po
```

### Custom Translation Dictionary

Bot-specific translations are stored in `emergency_bot/utils/translations.py`.

## Updating Translations

### Django Translations

1. Run the management command to extract translatable strings:

```bash
python manage.py update_translations
```

2. Edit the `.po` files in the `locale/<language>/LC_MESSAGES/` directories.

3. Compile the translations:

```bash
python manage.py update_translations --compile
```

### Bot Message Translations

To update bot message translations, edit the `TRANSLATIONS` dictionary in `emergency_bot/utils/translations.py`.

## Technical Implementation

1. **User Language Detection**: When a user interacts with the bot, their Telegram ID is used to look up their language preference.

2. **Middleware**: Django's `LocaleMiddleware` handles language selection for the web app based on user preferences.

3. **Translation Functions**: The `get_text()` function in `translations.py` provides translations for the bot messages.

## Adding a New Language

1. Add the new language code and name to the `LANGUAGES` list in `settings.py`.

2. Add the language to the `UserProfile` model's language choices.

3. Create translation files for the new language.

4. Add translations to the `TRANSLATIONS` dictionary in `translations.py`.

## Best Practices

1. Always use translation functions for user-facing text.
2. Test the bot with different language settings.
3. Ensure translations maintain the original meaning and tone.
4. Keep translations updated when adding new features.

## Known Limitations

- Some dynamic content (like agency names) may not be translated.
- Error messages from Telegram API are not translated. 