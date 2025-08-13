import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emergency_bot.settings')
django.setup()

# Import Django settings and models
from django.conf import settings
from bot.models import Location, Service, UserRequestLog
from emergency_bot.utils.translations import get_text, get_user_language, update_user_language

# Import Telegram libraries
from asgiref.sync import sync_to_async
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes, CallbackContext, CallbackQueryHandler
import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# States
CHOOSING_SERVICE = 1
CHOOSING_LANGUAGE = 2

# Language mapping
LANGUAGE_CHOICES = {
    'English 🇬🇧': 'en',
    'አማርኛ 🇪🇹': 'am',
    'Afaan Oromo 🇪🇹': 'om'
}

# Reverse mapping for displaying language names
LANGUAGE_DISPLAY = {
    'en': 'English 🇬🇧',
    'am': 'አማርኛ 🇪🇹',
    'om': 'Afaan Oromo 🇪🇹'
}

# Service Type to Human-friendly name mapping
service_type_display = {
    'hospital': 'Hospital',
    'police': 'Police',
    'ambulance': 'Ambulance',
    'women_child_affair': 'Women and Child Affair'
}

# Helper function to get user's language
async def get_user_lang(user_id):
    # Convert to async function
    language = await sync_to_async(get_user_language)(user_id)
    return language

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.effective_user.id)
    language = await get_user_lang(user_id)
    
    # Main keyboard with service choices and language button
    keyboard = [
        [
            get_text('hospital', language), 
            get_text('police', language)
        ],
        [
            get_text('ambulance', language), 
            get_text('women_child_affair', language)
        ],
        [get_text('language_button', language)]
    ]
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        get_text('welcome_message', language),
        reply_markup=reply_markup
    )
    
    return CHOOSING_SERVICE

# Command to change language
async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.effective_user.id)
    language = await get_user_lang(user_id)
    
    # Create language selection keyboard
    keyboard = [
        ['English 🇬🇧'],
        ['አማርኛ 🇪🇹'],
        ['Afaan Oromo 🇪🇹']
    ]
    
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        get_text('choose_language', language),
        reply_markup=reply_markup
    )
    
    return CHOOSING_LANGUAGE

# Handle language selection
async def select_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.effective_user.id)
    selected_language = update.message.text
    
    # Map the selected language to language code
    language_code = LANGUAGE_CHOICES.get(selected_language, 'en')
    
    # Update user's language preference in the database
    success = await sync_to_async(update_user_language)(user_id, language_code)
    
    # Get the updated language for response
    updated_language = await get_user_lang(user_id)
    
    # Create main keyboard with service choices
    keyboard = [
        [
            get_text('hospital', updated_language), 
            get_text('police', updated_language)
        ],
        [
            get_text('ambulance', updated_language), 
            get_text('women_child_affair', updated_language)
        ],
        [get_text('language_button', updated_language)]
    ]
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        get_text('language_changed', updated_language),
        reply_markup=reply_markup
    )
    
    return CHOOSING_SERVICE

# Handle Service Choice
async def choose_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.effective_user.id)
    language = await get_user_lang(user_id)
    user_choice = update.message.text
    
    # If user clicked the language button
    if user_choice == get_text('language_button', language):
        return await language_command(update, context)
    
    # Map the translated service name back to the internal key
    service_key = None
    for key, display_name in service_type_display.items():
        if user_choice == get_text(key, language):
            service_key = key
            break
    
    if not service_key:
        await update.message.reply_text(get_text('invalid_choice', language))
        return CHOOSING_SERVICE
    
    # Log user request (skipping for now)
    logger.info(f"User chose: {service_key}, skipping UserRequestLog")

    # Find service
    service = await sync_to_async(Service.objects.filter(service_type=service_key).first)()

    if service:
        location_link = f"https://maps.google.com/?q={service.location.latitude},{service.location.longitude}"
        service_name = get_text(service_key, language)
        
        response = (
            f"{get_text('nearby_service', language, service=service_name)}\n\n"
            f"*{get_text('name', language)}:* {service.name}\n"
            f"*{get_text('phone', language)}:* {service.phone_number}\n"
            f"*{get_text('description', language)}:* {service.description}\n"
            f"*{get_text('location', language)}:* [Google Maps]({location_link})"
        )
        await update.message.reply_text(response, parse_mode="Markdown")
    else:
        service_name = get_text(service_key, language)
        await update.message.reply_text(
            get_text('no_service_found', language, service=service_name)
        )

    return CHOOSING_SERVICE

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    language = await get_user_lang(user_id)
    
    await update.message.reply_text(get_text('help_message', language))

# Cancel command
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.effective_user.id)
    language = await get_user_lang(user_id)
    
    await update.message.reply_text(get_text('operation_cancelled', language))
    return ConversationHandler.END

def main() -> None:
    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Conversation handler for service selection
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_service)],
            CHOOSING_LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_language)],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CommandHandler('language', language_command),
            CommandHandler('help', help_command),
        ],
    )

    app.add_handler(conv_handler)
    
    # Add separate command handlers
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('language', language_command))

    print("Bot is running with language support...")
    app.run_polling()

if __name__ == '__main__':
    main()
