"""
Language bridge module to integrate the multilingual functionality with the main bot.
This module adapts the custom language implementation to work with the original bot structure.
"""

import os
import logging
import sys
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
from asgiref.sync import sync_to_async
from emergency_bot.utils.translations import get_text, get_user_language, update_user_language
from emergency_bot.accounts.models import UserProfile

# Add project root to path for language debug logging
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import and setup language debug logging
try:
    from language_debug_logging import setup_language_logging, get_language_logger, log_language_operation, log_user_language_change, log_database_operation
    # Initialize language logging
    setup_language_logging()
    logger = get_language_logger(__name__)
    logger.info("Language bridge module initialized with debug logging")
except ImportError as e:
    # Fallback to standard logging if debug logging not available
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.warning(f"Language debug logging not available, using standard logging: {e}")

# Configure standard logging as backup
standard_logger = logging.getLogger(__name__)
standard_logger.setLevel(logging.DEBUG)

# Define language options with emojis
LANGUAGE_OPTIONS = [
    ["English 🇬🇧", "አማርኛ 🇪🇹"],
    ["Afaan Oromo 🇪🇹"]
]

# Language mapping
LANGUAGE_CODES = {
    "English 🇬🇧": "en",
    "አማርኛ 🇪🇹": "am",
    "Afaan Oromo 🇪🇹": "om"
}

# Reverse language mapping
LANGUAGE_NAMES = {
    "en": "English 🇬🇧",
    "am": "አማርኛ 🇪🇹",
    "om": "Afaan Oromo 🇪🇹"
}

async def get_user_language_async(user_id):
    """Get the user's language preference asynchronously with comprehensive logging"""
    logger.debug(f"get_user_language_async called for user_id: {user_id}")
    
    try:
        # Convert user_id to string for consistency
        user_id_str = str(user_id)
        logger.debug(f"Converted user_id to string: {user_id_str}")
        
        # Log database operation attempt
        log_database_operation("SELECT", "UserProfile", user_id_str, ["language"], success=False)
        
        # Call the sync function asynchronously - use get_or_create to handle missing users
        logger.debug(f"Calling sync get_user_language_safe for user {user_id_str}")
        language = await sync_to_async(get_user_language_safe)(user_id_str)
        
        # Log successful database operation
        log_database_operation("SELECT", "UserProfile", user_id_str, ["language"], success=True)
        
        logger.info(f"Retrieved language '{language}' for user {user_id_str}")
        return language
        
    except Exception as e:
        # Log database operation failure
        log_database_operation("SELECT", "UserProfile", str(user_id), ["language"], success=False, error_msg=str(e))
        
        logger.error(f"Error getting user language for {user_id}: {e}", exc_info=True)
        logger.info(f"Defaulting to English for user {user_id}")
        return "en"  # Default to English on error


def get_user_language_safe(user_id):
    """Get user language, creating user profile if it doesn't exist"""
    try:
        user_profile, created = UserProfile.objects.get_or_create(
            telegram_id=user_id,
            defaults={'language': 'en'}
        )
        
        if created:
            logger.info(f"Created new user profile for telegram_id: {user_id}")
        
        return user_profile.language or 'en'
    except Exception as e:
        logger.error(f"Error in get_user_language_safe: {e}")
        return 'en'

async def update_user_language_async(user_id, language_code):
    """Update the user's language preference asynchronously with comprehensive logging"""
    logger.info(f"update_user_language_async called for user {user_id} with language {language_code}")
    
    try:
        # Get current language for comparison
        current_language = await get_user_language_async(user_id)
        logger.debug(f"Current language for user {user_id}: {current_language}")
        
        # Make sure user_id is a string
        user_id_str = str(user_id)
        logger.debug(f"Converted user_id to string: {user_id_str}")
        
        # Check if language_code is valid
        valid_languages = ['en', 'am', 'om']
        if language_code not in valid_languages:
            error_msg = f"Invalid language code: {language_code}. Valid codes: {valid_languages}"
            logger.error(error_msg)
            log_user_language_change(user_id_str, current_language, language_code, success=False, error_msg=error_msg)
            return False
        
        # Check if language is already set to avoid unnecessary database operations
        if current_language == language_code:
            logger.info(f"Language already set to {language_code} for user {user_id_str}, no update needed")
            log_user_language_change(user_id_str, current_language, language_code, success=True)
            return True
        
        # Log database operation attempt
        log_database_operation("UPDATE", "UserProfile", user_id_str, ["language"], success=False)
        logger.debug(f"Attempting to update language from {current_language} to {language_code}")
        
        # Call the sync function with sync_to_async - use new method for shared hosting
        logger.debug(f"Calling sync update_user_language for user {user_id_str}")
        success = await sync_to_async(update_user_language_with_tracking)(user_id_str, language_code)
        
        if success:
            # Log successful update
            log_database_operation("UPDATE", "UserProfile", user_id_str, ["language"], success=True)
            log_user_language_change(user_id_str, current_language, language_code, success=True)
            logger.info(f"Successfully updated language for user {user_id_str} from {current_language} to {language_code}")
            
            # Send WebSocket notification to mini app
            await notify_language_change(user_id_str, language_code)
        else:
            # Log failed update
            error_msg = "update_user_language returned False"
            log_database_operation("UPDATE", "UserProfile", user_id_str, ["language"], success=False, error_msg=error_msg)
            log_user_language_change(user_id_str, current_language, language_code, success=False, error_msg=error_msg)
            logger.error(f"Failed to update language for user {user_id_str}: {error_msg}")
        
        return success
        
    except Exception as e:
        # Log exception details
        error_msg = f"Exception in update_user_language_async: {str(e)}"
        log_database_operation("UPDATE", "UserProfile", str(user_id), ["language"], success=False, error_msg=error_msg)
        log_user_language_change(str(user_id), current_language if 'current_language' in locals() else 'unknown', language_code, success=False, error_msg=error_msg)
        
        logger.error(f"Error in update_user_language_async for user {user_id}: {e}", exc_info=True)
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False


def update_user_language_with_tracking(user_id, language_code):
    """Update user language with tracking for shared hosting (sync function)"""
    try:
        # Get or create user profile if it doesn't exist
        user_profile, created = UserProfile.objects.get_or_create(
            telegram_id=user_id,
            defaults={'language': 'en'}  # Default language
        )
        
        if created:
            logger.info(f"Created new user profile for telegram_id: {user_id}")
        
        return user_profile.update_language_with_sync(language_code)
    except Exception as e:
        logger.error(f"Error updating user language with tracking: {e}")
        return False


async def notify_language_change(user_id, language_code):
    """Send WebSocket notification about language change to mini app (fallback for advanced hosting)"""
    try:
        from channels.layers import get_channel_layer
        from datetime import datetime
        
        channel_layer = get_channel_layer()
        if channel_layer:
            group_name = f"language_sync_{user_id}"
            await channel_layer.group_send(
                group_name,
                {
                    "type": "language_changed",
                    "language": language_code,
                    "timestamp": datetime.now().isoformat(),
                    "source": "telegram"
                }
            )
            logger.info(f"Sent language change notification to WebSocket for user {user_id}")
        else:
            logger.warning("Channel layer not available, using database polling instead")
    except Exception as e:
        logger.warning(f"WebSocket notification failed (using database polling): {e}")

async def language_selection_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Command to show language selection options"""
    user = update.effective_user
    current_lang = await get_user_language_async(user.id)
    
    # Create keyboard with language options
    keyboard = []
    for row in LANGUAGE_OPTIONS:
        keyboard_row = []
        for lang_name in row:
            keyboard_row.append(InlineKeyboardButton(lang_name, callback_data=f"setlang_{LANGUAGE_CODES.get(lang_name, 'en')}"))
        keyboard.append(keyboard_row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        get_text('choose_language', current_lang),
        reply_markup=reply_markup
    )

async def language_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle language selection via callback query with comprehensive logging"""
    query = update.callback_query
    user = query.from_user
    
    logger.info(f"language_button_callback triggered by user {user.id} with data: {query.data}")
    
    try:
        # Answer the callback query first
        await query.answer()
        logger.debug(f"Answered callback query for user {user.id}")
        
        # Extract language code from callback data
        try:
            lang_code = query.data.split('_')[1]
            logger.debug(f"Extracted language code: {lang_code} from callback data: {query.data}")
        except (IndexError, AttributeError) as e:
            error_msg = f"Failed to extract language code from callback data: {query.data}"
            logger.error(error_msg)
            await query.edit_message_text(
                "Invalid language selection. Please try again."
            )
            return
        
        # Validate language code
        valid_languages = ['en', 'am', 'om']
        if lang_code not in valid_languages:
            error_msg = f"Invalid language code: {lang_code}"
            logger.error(error_msg)
            await query.edit_message_text(
                f"Invalid language selection: {lang_code}. Please try again."
            )
            return
        
        logger.info(f"User {user.id} attempting to change language to: {lang_code}")
        
        # Update user's language preference
        logger.debug(f"Calling update_user_language_async for user {user.id}")
        success = await update_user_language_async(user.id, lang_code)
        logger.info(f"Language update result for user {user.id}: success={success}")
        
        if success:
            logger.info(f"Language successfully updated to {lang_code} for user {user.id}")
            
            # Send confirmation message in the new language
            try:
                confirmation_text = get_text('language_changed', lang_code)
                logger.debug(f"Sending confirmation message: {confirmation_text}")
                await query.edit_message_text(confirmation_text)
                logger.debug(f"Confirmation message sent successfully")
            except Exception as e:
                logger.error(f"Error sending confirmation message: {e}", exc_info=True)
            
            # Get URLs for web app buttons - use the same URLs as in bot.py
            try:
                from emergency_bot.telegram_bot.bot import WEBAPP_URL, get_report_url
                logger.debug(f"Retrieved URLs: WEBAPP_URL={WEBAPP_URL}")
            except ImportError as e:
                logger.error(f"Error importing URLs from bot.py: {e}")
                WEBAPP_URL = "https://gaddisa.hdmsoftwaresolutions.com"
                # Define fallback function for get_report_url
                def get_report_url(user_id=None, language=None):
                    url = "https://gaddisa.hdmsoftwaresolutions.com/webapp/report.html"
                    params = []
                    if user_id:
                        params.append(f"user_id={user_id}")
                    if language:
                        params.append(f"lang={language}")
                    if params:
                        url += "?" + "&".join(params)
                    return url
                logger.debug(f"Using fallback URLs: WEBAPP_URL={WEBAPP_URL}")
            
            # Create a new message with the main menu in the selected language
            try:
                logger.debug(f"Creating main menu keyboard in language: {lang_code}")
                keyboard = [
                    [InlineKeyboardButton(
                        "🏥 " + get_text('available_services', lang_code), 
                        web_app=WebAppInfo(url=WEBAPP_URL)
                    )],
                    [InlineKeyboardButton(
                        "📞 " + get_text('emergency_numbers', lang_code), 
                        callback_data="emergency_call_options"
                    )],
                    [InlineKeyboardButton(
                        "📝 " + get_text('report_emergency', lang_code), 
                        web_app=WebAppInfo(url=get_report_url(user.id, lang_code))
                    )],
                    [InlineKeyboardButton(
                        "❓ " + get_text('how_to_use_bot', lang_code), 
                        callback_data="show_help"
                    )],
                    [InlineKeyboardButton(
                        "🛡️ " + get_text('safety_info', lang_code),
                        callback_data="show_safety_info"
                    )],
                    [InlineKeyboardButton(
                        "🌐 " + get_text('language_button', lang_code), 
                        callback_data="change_language"
                    )]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                logger.debug(f"Created keyboard with {len(keyboard)} rows")
                
                # Send a new message with the main menu
                welcome_text = get_text('welcome_message', lang_code)
                logger.debug(f"Sending main menu message: {welcome_text}")
                await context.bot.send_message(
                    chat_id=user.id,
                    text=welcome_text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
                logger.info(f"Main menu sent successfully to user {user.id} in language {lang_code}")
                
            except Exception as e:
                logger.error(f"Error creating/sending main menu: {e}", exc_info=True)
                await context.bot.send_message(
                    chat_id=user.id,
                    text=f"Language changed to {LANGUAGE_NAMES.get(lang_code, lang_code)}. Use /start to see the main menu.",
                )
        else:
            # Error message if language update failed
            error_msg = "Error updating language preference. Please try again."
            logger.error(f"Language update failed for user {user.id}, showing error message")
            await query.edit_message_text(error_msg)
            
    except Exception as e:
        error_msg = f"Exception in language_button_callback for user {user.id}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        try:
            await query.edit_message_text(
                "An error occurred while updating your language preference. Please try again with /start."
            )
        except Exception as edit_error:
            logger.error(f"Failed to send error message to user {user.id}: {edit_error}")
            
            # Try sending a new message if editing fails
            try:
                await context.bot.send_message(
                    chat_id=user.id,
                    text="An error occurred while updating your language preference. Please try again with /start."
                )
            except Exception as send_error:
                logger.error(f"Failed to send fallback message to user {user.id}: {send_error}")

def setup_language_handlers(application):
    """Add language handlers to the main application"""
    from telegram.ext import CommandHandler, CallbackQueryHandler
    
    # Add language command handler
    application.add_handler(CommandHandler("language", language_selection_command))
    
    # Add callback handler for language selection
    application.add_handler(CallbackQueryHandler(language_button_callback, pattern=r"^setlang_"))
    
    logger.info("Language handlers added to the application")
    
    return application

async def translate_service_type(service_type, language):
    """Translate service types to the user's language"""
    service_keys = {
        'hospital': 'hospital',
        'police': 'police',
        'ambulance': 'ambulance',
        'women_child_affair': 'women_child_affair'
    }
    
    key = service_keys.get(service_type.lower().replace(' ', '_'), service_type)
    return get_text(key, language)