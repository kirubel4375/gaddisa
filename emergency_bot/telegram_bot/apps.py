from django.apps import AppConfig


class TelegramBotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'emergency_bot.telegram_bot'
    verbose_name = 'Telegram Bot'

    def ready(self):
        """
        Initialize the app when Django starts.
        This is a good place to initialize the bot application if needed.
        """
        # Import signals or other initialization code here
        # We don't initialize the bot here to avoid circular imports
        # The bot will be initialized when the webhook is called
        pass 