from django.core.management.base import BaseCommand
from django.conf import settings
import os
import logging

class Command(BaseCommand):
    help = 'Runs the Telegram bot'

    def add_arguments(self, parser):
        parser.add_argument(
            '--webapp-url',
            type=str,
            help='URL for the web app (e.g., https://example.com)',
        )

    def handle(self, *args, **options):
        # Set the webapp URL if provided
        if options['webapp_url']:
            os.environ['WEBAPP_URL'] = options['webapp_url']
            self.stdout.write(self.style.SUCCESS(f"Using WebApp URL: {options['webapp_url']}"))
        
        # Import here to ensure Django is fully loaded
        from emergency_bot.telegram_bot.bot import run_bot
        
        self.stdout.write(self.style.SUCCESS('Starting Telegram bot...'))
        try:
            # Run the bot
            run_bot()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Bot stopped by user'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error running bot: {e}')) 