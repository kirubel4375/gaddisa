import os
import subprocess
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Extract translatable messages and compile translations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--compile', 
            action='store_true', 
            help='Compile translations after extraction'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting translation process...'))
        
        # Paths
        locale_dir = os.path.join(settings.BASE_DIR, 'locale')
        
        # Make sure locale directory exists
        if not os.path.exists(locale_dir):
            os.makedirs(locale_dir)
            self.stdout.write(self.style.SUCCESS(f'Created locale directory at {locale_dir}'))
        
        # Extract messages
        self.stdout.write(self.style.WARNING('Extracting messages...'))
        try:
            # Use django's makemessages command
            subprocess.run([
                'django-admin', 'makemessages', 
                '-l', 'en',
                '-l', 'am',
                '-l', 'om',
                '--ignore=env/*',
                '--ignore=venv/*',
                '--ignore=staticfiles/*',
            ], check=True)
            self.stdout.write(self.style.SUCCESS('Successfully extracted messages'))
        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f'Error extracting messages: {str(e)}'))
            return
        
        if options['compile']:
            self.stdout.write(self.style.WARNING('Compiling translations...'))
            try:
                # Use django's compilemessages command
                subprocess.run(['django-admin', 'compilemessages'], check=True)
                self.stdout.write(self.style.SUCCESS('Successfully compiled translations'))
            except subprocess.CalledProcessError as e:
                self.stdout.write(self.style.ERROR(f'Error compiling translations: {str(e)}'))
                return
        
        self.stdout.write(self.style.SUCCESS('Translation process completed.'))
        self.stdout.write(self.style.WARNING(
            '\nTo manually translate files:'
            '\n1. Edit the .po files in the locale/<language>/LC_MESSAGES/ directories'
            '\n2. Run "python manage.py update_translations --compile" to compile the translations'
        )) 