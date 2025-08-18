import logging
import os
import sys
import requests
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from django.conf import settings
from emergency_bot.accounts.models import UserProfile
from asgiref.sync import sync_to_async

# Import language bridge
from emergency_bot.telegram_bot.language_bridge import (
    get_user_language_async,
    update_user_language_async,
    language_selection_command,
    language_button_callback,
    setup_language_handlers,
    translate_service_type,
    get_text
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get the bot token from settings
BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN

def get_webapp_url():
    """Get the WebApp URL from multiple possible sources, in order of reliability"""
    
    # Check webapp_url.txt first (for cPanel deployment)
    webapp_url_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "webapp_url.txt")
    if os.path.exists(webapp_url_path):
        try:
            with open(webapp_url_path, 'r') as f:
                url = f.read().strip()
                if url and (url.startswith("http://") or url.startswith("https://")):
                    logger.info(f"Using URL from webapp_url.txt: {url}")
                    return url
        except Exception as e:
            logger.warning(f"Error reading webapp_url.txt: {e}")
    
    # Check environment variable
    env_url = os.environ.get('WEBAPP_URL')
    if env_url and (env_url.startswith("http://") or env_url.startswith("https://")):
        logger.info(f"Using URL from environment: {env_url}")
        return env_url
    
    # Fallback to a default URL
    default_url = "https://gaddisa.hdmsoftwaresolutions.com"
    logger.info(f"Using default URL: {default_url}")
    return default_url

def get_report_url(user_id=None, language=None):
    """Get the URL for the report page with optional user_id and language parameters"""
    base_url = get_webapp_url()
    # Remove any trailing paths like /index.html from base_url
    if base_url.endswith('/index.html'):
        base_url = base_url[:-11]  # Remove '/index.html'
    elif base_url.endswith('/index.html/'):
        base_url = base_url[:-12]  # Remove '/index.html/'
    
    report_url = f"{base_url}/webapp/report.html"
    
    # Add query parameters if provided
    params = []
    if user_id:
        params.append(f"user_id={user_id}")
    if language:
        params.append(f"lang={language}")
    
    if params:
        report_url += "?" + "&".join(params)
    
    logger.info(f"Using report URL: {report_url}")
    return report_url

def get_agencies_url():
    """Get the URL for the agencies page"""
    base_url = get_webapp_url()
    # Remove any trailing paths like /index.html from base_url
    if base_url.endswith('/index.html'):
        base_url = base_url[:-11]  # Remove '/index.html'
    elif base_url.endswith('/index.html/'):
        base_url = base_url[:-12]  # Remove '/index.html/'
    
    agencies_url = f"{base_url}/webapp/agencies.html"
    logger.info(f"Using agencies URL: {agencies_url}")
    return agencies_url

# Get the WebApp URL
WEBAPP_URL = get_webapp_url()
AGENCIES_URL = get_agencies_url()
logger.info(f"Using WebApp URL: {WEBAPP_URL}")
logger.info(f"Using Agencies URL: {AGENCIES_URL}")

# Function to create a WebAppInfo button with retry logic
def create_webapp_button(user_id):
    """Create a WebApp button with error checking, always using the latest WebApp URL"""
    # Get the latest URL
    url = f"{get_webapp_url()}"
    
    # Add user_id parameter if not None
    if user_id:
        url = f"{url}?user_id={user_id}"
    
    logger.info(f"Creating WebApp button with URL: {url}")
    
    # Create WebAppInfo without testing the URL to avoid delays
    return WebAppInfo(url=url)

async def get_or_create_user(telegram_id, first_name=None):
    """Get or create a user profile, returns (user_profile, is_new_user)"""
    try:
        logger.info(f"Looking up user with telegram_id: {telegram_id}")
        
        user_profile, created = await sync_to_async(UserProfile.objects.get_or_create)(telegram_id=telegram_id)
        await sync_to_async(user_profile.update_last_active)()
        
        # Log if new user
        if created:
            logger.info(f"Created new user profile for Telegram ID: {telegram_id}, Name: {first_name}")
        else:
            logger.info(f"Found existing user profile for Telegram ID: {telegram_id}")
            
        return user_profile, created
    except Exception as e:
        logger.error(f"Error getting/creating user: {e}", exc_info=True)
        # Return None values to indicate error
        return None, False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    try:
        user = update.effective_user
        logger.info(f"Start command received from user: {user.id} ({user.first_name})")
        
        # Get or create user profile
        user_profile, is_new_user = await get_or_create_user(
            user.id, 
            first_name=user.first_name
        )
        logger.info(f"User profile: {user_profile}, is_new_user: {is_new_user}")
        
        # Get user's language preference
        language = await get_user_language_async(user.id)
        
        # If new user, show language selection and GDPR consent
        if is_new_user:
            logger.info(f"New user, showing welcome message")
            return await welcome_new_user(update, context)
            
        # Create keyboard with WebApp button - use direct URL without parameters for testing
        try:
            keyboard = [
                [InlineKeyboardButton(
                    "🏥 " + get_text('available_services', language), 
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )],
                [InlineKeyboardButton(
                    "📞 " + get_text('emergency_numbers', language), 
                    callback_data="emergency_call_options"
                )],
                [InlineKeyboardButton(
                    "📝 " + get_text('report_emergency', language), 
                    web_app=WebAppInfo(url=get_report_url(user.id, language))
                )],
                [InlineKeyboardButton(
                    "❓ " + get_text('how_to_use_bot', language), 
                    callback_data="show_help"
                )],
                [InlineKeyboardButton(
                    "🛡️ " + get_text('safety_info', language),
                    callback_data="show_safety_info"
                )],
                [InlineKeyboardButton(
                    "🌐 " + get_text('language_button', language), 
                    callback_data="change_language"
                )]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_html(
                get_text('welcome_message', language),
                reply_markup=reply_markup,
            )
            logger.info(f"Sent reply message with WebApp button")
        except Exception as e:
            logger.error(f"Error creating WebApp button: {e}", exc_info=True)
            # Fallback without WebApp button
            await update.message.reply_html(
                f"Hi {user.first_name}! " + get_text('welcome_message', language)
            )
            logger.info(f"Sent fallback message without WebApp button")
    except Exception as e:
        logger.error(f"Error in start command: {e}", exc_info=True)
        # Try to send a basic response
        try:
            await update.message.reply_text("Sorry, I encountered an error. Please try again later.")
        except:
            pass

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Simple test command that doesn't rely on database or complex functionality."""
    try:
        user = update.effective_user
        logger.info(f"Test command received from user: {user.id} ({user.first_name})")
        
        await update.message.reply_text(
            f"Hello {user.first_name}! This is a test response.\n\n"
            f"Your user ID: {user.id}\n"
            f"Bot is working correctly if you see this message."
        )
        logger.info("Test command completed successfully")
    except Exception as e:
        logger.error(f"Error in test command: {e}", exc_info=True)
        try:
            await update.message.reply_text("Error in test command. Check logs for details.")
        except:
            pass

async def welcome_new_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Welcome a new user with language selection."""
    user = update.effective_user
    
    # Create language selection keyboard using the language bridge approach
    keyboard = []
    for row in [["English 🇬🇧", "አማርኛ 🇪🇹"], ["Afaan Oromo 🇪🇹"]]:
        keyboard_row = []
        for lang_name in row:
            if lang_name == "English 🇬🇧":
                keyboard_row.append(InlineKeyboardButton(lang_name, callback_data="setlang_en"))
            elif lang_name == "አማርኛ 🇪🇹":
                keyboard_row.append(InlineKeyboardButton(lang_name, callback_data="setlang_am"))
            elif lang_name == "Afaan Oromo 🇪🇹":
                keyboard_row.append(InlineKeyboardButton(lang_name, callback_data="setlang_om"))
        keyboard.append(keyboard_row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_html(
        f"<b>Welcome {user.first_name}!</b>\n\n"
        f"Thank you for using the Emergency Reporting Bot. "
        f"First, please select your preferred language:",
        reply_markup=reply_markup,
    )

async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle language selection callback."""
    query = update.callback_query
    await query.answer()  # Answer the callback query
    
    user = query.from_user
    selected_lang = query.data.split('_')[1]  # Extract language code
    
    # Update user profile with selected language
    try:
        user_profile = UserProfile.objects.get(telegram_id=user.id)
        user_profile.language = selected_lang
        user_profile.save(update_fields=["language"])
        
        # Now show GDPR consent
        keyboard = [
            [InlineKeyboardButton("I Agree", callback_data="consent_agree")],
            [InlineKeyboardButton("Learn More", callback_data="consent_more")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        language_names = {"en": "English", "am": "Amharic", "om": "Afaan Oromo"}
        language_name = language_names.get(selected_lang, "Unknown")
        
        await query.edit_message_text(
            f"Language set to: {language_name}\n\n"
            f"<b>Data Privacy Consent</b>\n\n"
            f"To use this emergency reporting service, we need to collect some information "
            f"like your Telegram ID and incident reports you submit. This data is used only "
            f"to provide you with emergency services. You can request data deletion at any time.\n\n"
            f"Do you agree to these terms?",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Error updating language: {e}")
        await query.edit_message_text(
            "Sorry, there was an error setting your language. Please try again with /start"
        )

async def handle_consent_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user's response to consent request."""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    response = query.data.split('_')[1]
    
    if response == "agree":
        # Update user profile with consent
        try:
            user_profile = UserProfile.objects.get(telegram_id=user.id)
            user_profile.grant_consent()
            
            # Get user's language preference
            language = await get_user_language_async(user.id)
            
            # Create keyboard with WebApp button
            keyboard = [
                [InlineKeyboardButton(
                    "🏥 " + get_text('available_services', language), 
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )],
                [InlineKeyboardButton(
                    "📞 " + get_text('emergency_numbers', language), 
                    callback_data="emergency_call_options"
                )],
                [InlineKeyboardButton(
                    "📝 " + get_text('report_emergency', language), 
                    web_app=WebAppInfo(url=get_report_url(user.id, language))
                )],
                [InlineKeyboardButton(
                    "❓ " + get_text('how_to_use_bot', language), 
                    callback_data="show_help"
                )],
                [InlineKeyboardButton(
                    "🛡️ " + get_text('safety_info', language),
                    callback_data="show_safety_info"
                )],
                [InlineKeyboardButton(
                    "🌐 " + get_text('language_button', language), 
                    callback_data="change_language"
                )]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"Thank you for your consent! You're now ready to use the Emergency Reporting App.\n\n"
                f"Use the button below to open the app. You can report incidents, "
                f"find nearby support agencies, and manage your profile.",
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error updating consent: {e}")
            await query.edit_message_text(
                "Sorry, there was an error saving your consent. Please try again with /start"
            )
    elif response == "more":
        # Show more detailed privacy information
        keyboard = [
            [InlineKeyboardButton("I Agree", callback_data="consent_agree")],
            [InlineKeyboardButton("Decline", callback_data="consent_decline")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "<b>Privacy Policy Details</b>\n\n"
            "The Emergency Reporting System collects and processes the following data:\n"
            "• Your Telegram ID to identify you\n"
            "• Your language preference\n"
            "• Incident reports you submit (including location)\n"
            "• Voice notes (if you choose to record them)\n\n"
            "This data is used only to:\n"
            "• Provide emergency reporting services\n"
            "• Connect you with appropriate support agencies\n"
            "• Improve the service based on aggregated statistics\n\n"
            "You have the right to:\n"
            "• Access your data\n"
            "• Request deletion of your data\n"
            "• Withdraw consent at any time\n\n"
            "Do you agree to these terms?",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    elif response == "decline":
        await query.edit_message_text(
            "You have declined to provide consent. Unfortunately, you cannot use the "
            "Emergency Reporting System without consenting to our data processing.\n\n"
            "You can restart the process at any time with /start if you change your mind."
        )

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Allow existing users to change their language."""
    query = update.callback_query
    await query.answer()
    
    # Create language selection keyboard using the language bridge approach
    keyboard = []
    for row in [["English 🇬🇧", "አማርኛ 🇪🇹"], ["Afaan Oromo 🇪🇹"]]:
        keyboard_row = []
        for lang_name in row:
            if lang_name == "English 🇬🇧":
                keyboard_row.append(InlineKeyboardButton(lang_name, callback_data="setlang_en"))
            elif lang_name == "አማርኛ 🇪🇹":
                keyboard_row.append(InlineKeyboardButton(lang_name, callback_data="setlang_am"))
            elif lang_name == "Afaan Oromo 🇪🇹":
                keyboard_row.append(InlineKeyboardButton(lang_name, callback_data="setlang_om"))
        keyboard.append(keyboard_row)
    
    keyboard.append([InlineKeyboardButton("← Back", callback_data="back_to_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Get user's language for the prompt
    user_id = query.from_user.id
    language = await get_user_language_async(user_id)
    
    await query.edit_message_text(
        get_text('choose_language', language),
        reply_markup=reply_markup
    )

async def emergency_call_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show emergency call options dropdown when the emergency call button is clicked."""
    query = update.callback_query
    
    try:
        await query.answer()
        
        user = query.from_user
        logger.info(f"Emergency call options requested by user: {user.id}")
        
        # Get user's language preference with error handling
        try:
            language = await get_user_language_async(user.id)
            logger.debug(f"Retrieved language '{language}' for user {user.id}")
        except Exception as e:
            logger.error(f"Error getting user language for {user.id}: {e}")
            language = 'en'  # Default to English if language retrieval fails
        
        # Validate language code
        if language not in ['en', 'am', 'om']:
            logger.warning(f"Invalid language code '{language}' for user {user.id}, defaulting to 'en'")
            language = 'en'
        
        # Create keyboard with emergency call options (using callback_data instead of tel: URLs)
        try:
            keyboard = [
                [InlineKeyboardButton("🚨 " + get_text('call_7711_text', language), callback_data="call_7711")],
                [InlineKeyboardButton("👮 " + get_text('call_999_text', language), callback_data="call_999")],
                [InlineKeyboardButton("🚑 " + get_text('call_907_text', language), callback_data="call_907")],
                [InlineKeyboardButton("🔥 " + get_text('call_939_text', language), callback_data="call_939")],
                [InlineKeyboardButton("🏥 " + get_text('call_911_text', language), callback_data="call_911")],
                [InlineKeyboardButton("◀️ " + get_text('back_to_menu', language), callback_data="back_to_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            logger.debug(f"Created emergency numbers keyboard with {len(keyboard)} buttons for language '{language}'")
        except Exception as e:
            logger.error(f"Error creating emergency numbers keyboard: {e}")
            # Fallback keyboard with basic options
            keyboard = [
                [InlineKeyboardButton("🚨 Call 7711 - Emergency", callback_data="call_7711")],
                [InlineKeyboardButton("👮 Call 999 - Police", callback_data="call_999")],
                [InlineKeyboardButton("🚑 Call 907 - Ambulance", callback_data="call_907")],
                [InlineKeyboardButton("🔥 Call 939 - Fire", callback_data="call_939")],
                [InlineKeyboardButton("🏥 Call 911 - Emergency", callback_data="call_911")],
                [InlineKeyboardButton("◀️ Back to Menu", callback_data="back_to_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            logger.debug("Using fallback keyboard due to translation error")
        
        # Send the emergency numbers menu
        try:
            menu_text = get_text('emergency_numbers_menu', language)
            logger.debug(f"Retrieved menu text for language '{language}': {menu_text[:50]}...")
            
            await query.edit_message_text(
                menu_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            logger.info(f"Emergency numbers menu sent successfully to user {user.id} in language '{language}'")
        except Exception as e:
            logger.error(f"Error sending emergency numbers menu: {e}")
            # Fallback with simple text
            try:
                fallback_text = f"📞 {get_text('emergency_numbers', language)}\n\nChoose an emergency service to call:"
                await query.edit_message_text(
                    fallback_text,
                    reply_markup=reply_markup
                )
                logger.info(f"Sent fallback emergency numbers menu to user {user.id}")
            except Exception as fallback_error:
                logger.error(f"Fallback emergency numbers menu also failed: {fallback_error}")
                # Try sending a new message if editing fails
                try:
                    await context.bot.send_message(
                        chat_id=user.id,
                        text="📞 Emergency Numbers\n\nChoose an emergency service to call:",
                        reply_markup=reply_markup
                    )
                    logger.info(f"Sent new emergency numbers message to user {user.id}")
                except Exception as send_error:
                    logger.error(f"Even sending new message failed: {send_error}")
                
    except Exception as e:
        logger.error(f"Critical error in emergency_call_options for user {query.from_user.id if query and query.from_user else 'unknown'}: {e}", exc_info=True)
        # Last resort fallback
        try:
            await query.edit_message_text(
                "Emergency numbers are temporarily unavailable. Please call 7711 directly for emergency services."
            )
        except:
            # If all else fails, try sending a new message
            try:
                await context.bot.send_message(
                    chat_id=query.from_user.id,
                    text="Emergency numbers are temporarily unavailable. Please call 7711 directly for emergency services."
                )
            except Exception as final_error:
                logger.error(f"Even final fallback failed: {final_error}")

async def handle_emergency_call(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle emergency number button clicks and provide call instructions."""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    emergency_number = query.data.split('_')[1]  # Extract number from callback_data
    
    # Get user's language preference
    try:
        language = await get_user_language_async(user.id)
    except Exception as e:
        logger.error(f"Error getting user language for {user.id}: {e}")
        language = 'en'
    
    # Validate language code
    if language not in ['en', 'am', 'om']:
        language = 'en'
    
    # Create message based on emergency number
    emergency_info = {
        '7711': {
            'en': '🚨 **Emergency Services - 7711**\n\nTo call Emergency Services, dial **7711** on your phone.\n\nThis is the main emergency number for immediate assistance.',
            'am': '🚨 **የአደጋ ጊዜ አገልግሎቶች - 7711**\n\nየአደጋ ጊዜ አገልግሎቶችን ለመደወል በስልክዎ **7711** ይደውሉ።\n\nይህ ለአፋጣኝ እርዳታ ዋናው የአደጋ ጊዜ ቁጥር ነው።',
            'om': '🚨 **Tajaajila Balaa - 7711**\n\nTajaajila Balaa bilbiluuf bilbila keessan irraa **7711** bilbilaa.\n\nKunis gargaarsa hatattamaa argachuuf lakkoofsa balaa jalqabaa dha.'
        },
        '999': {
            'en': '👮 **Police - 999**\n\nTo call the Police, dial **999** on your phone.\n\nUse this number for crimes, emergencies requiring police response.',
            'am': '👮 **ፖሊስ - 999**\n\nፖሊስን ለመደወል በስልክዎ **999** ይደውሉ।\n\nይህን ቁጥር ለወንጀሎች፣ የፖሊስ ምላሽ ለሚፈልጉ አደጋዎች ይጠቀሙ።',
            'om': '👮 **Poolisii - 999**\n\nPoolisii bilbiluuf bilbila keessan irraa **999** bilbilaa.\n\nLakkoofsa kana yakkamoota, muddaalee deebii poolisii barbaadaniif fayyadamaa.'
        },
        '907': {
            'en': '🚑 **Ambulance - 907**\n\nTo call an Ambulance, dial **907** on your phone.\n\nUse this number for medical emergencies and urgent health issues.',
            'am': '🚑 **አምቡላንስ - 907**\n\nአምቡላንስን ለመደወል በስልክዎ **907** ይደውሉ።\n\nይህን ቁጥር ለጤና አደጋዎች እና አስቸኳይ ጤና ችግሮች ይጠቀሙ።',
            'om': '🚑 **Ambulaansii - 907**\n\nAmbulaansii bilbiluuf bilbila keessan irraa **907** bilbilaa.\n\nLakkoofsa kana muddaa fayyaa fi dhimma fayyaa ariifachiisaaf fayyadamaa.'
        },
        '939': {
            'en': '🔥 **Fire Department - 939**\n\nTo call the Fire Department, dial **939** on your phone.\n\nUse this number for fires, gas leaks, and related emergencies.',
            'am': '🔥 **እሳት አደጋ መከላከያ - 939**\n\nየእሳት አደጋ መከላከያን ለመደወል በስልክዎ **939** ይደውሉ።\n\nይህን ቁጥር ለእሳት፣ ለጋዝ መስሪያ እና ተዛማጅ አደጋዎች ይጠቀሙ።',
            'om': '🔥 **Ibidda Dhaamsuu - 939**\n\nIbidda Dhaamsuu bilbiluuf bilbila keessan irraa **939** bilbilaa.\n\nLakkoofsa kana ibidda, gaazii dhangala\'aa fi muddaalee wal qabataniif fayyadamaa.'
        },
        '911': {
            'en': '🏥 **General Emergency - 911**\n\nTo call General Emergency services, dial **911** on your phone.\n\nUse this number for general emergencies and urgent situations.',
            'am': '🏥 **አጠቃላይ አደጋ - 911**\n\nአጠቃላይ የአደጋ ጊዜ አገልግሎቶችን ለመደወል በስልክዎ **911** ይደውሉ።\n\nይህን ቁጥር ለአጠቃላይ አደጋዎች እና አስቸኳይ ሁኔታዎች ይጠቀሙ።',
            'om': '🏥 **Balaa Waliigalaa - 911**\n\nTajaajila Balaa Waliigalaa bilbiluuf bilbila keessan irraa **911** bilbilaa.\n\nLakkoofsa kana balaa waliigalaa fi haalawwan ariifachiisaaf fayyadamaa.'
        }
    }
    
    # Get the message for this emergency number and language
    message_text = emergency_info.get(emergency_number, emergency_info['7711']).get(language, emergency_info['7711']['en'])
    
    # Create back button
    keyboard = [
        [InlineKeyboardButton("◀️ " + get_text('back_to_menu', language), callback_data="emergency_call_options")],
        [InlineKeyboardButton("🏠 " + get_text('back_to_menu', language).replace('Menu', 'Home'), callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        logger.info(f"Emergency number {emergency_number} information sent to user {user.id} in language {language}")
    except Exception as e:
        logger.error(f"Error sending emergency number info: {e}")
        # Fallback
        await query.edit_message_text(
            f"📞 Call {emergency_number}\n\nDial {emergency_number} on your phone for emergency services.",
            reply_markup=reply_markup
        )

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return to the main menu."""
    query = update.callback_query
    await query.answer()
    user = query.from_user
    
    # Get user's language preference
    language = await get_user_language_async(user.id)
    
    # Create keyboard with WebApp button
    keyboard = [
        [InlineKeyboardButton(
            "🏥 " + get_text('available_services', language), 
            web_app=WebAppInfo(url=WEBAPP_URL)
        )],
        [InlineKeyboardButton(
            "📞 " + get_text('emergency_numbers', language), 
            callback_data="emergency_call_options"
        )],
        [InlineKeyboardButton(
            "📝 " + get_text('report_emergency', language), 
            web_app=WebAppInfo(url=REPORT_URL)
        )],
        [InlineKeyboardButton(
            "❓ " + get_text('how_to_use_bot', language), 
            callback_data="show_help"
        )],
        [InlineKeyboardButton(
            "🛡️ " + get_text('safety_info', language),
            callback_data="show_safety_info"
        )],
        [InlineKeyboardButton(
            "🌐 " + get_text('language_button', language), 
            callback_data="change_language"
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        get_text('welcome_message', language),
        reply_markup=reply_markup,
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    user = update.effective_user
    user_language = await get_user_language_async(user.id)
    
    help_text = get_text('help_text', user_language)
    await update.message.reply_html(help_text)

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Allow users to change language via command."""
    # Create language selection keyboard
    keyboard = [
        [
            InlineKeyboardButton("English 🇬🇧", callback_data="setlang_en"),
            InlineKeyboardButton("አማርኛ 🇪🇹", callback_data="setlang_am")
        ],
        [
            InlineKeyboardButton("Afaan Oromo 🇪🇹", callback_data="setlang_om")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Please select your preferred language:",
        reply_markup=reply_markup
    )

async def privacy_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show privacy policy information."""
    privacy_text = (
        "<b>Privacy Policy</b>\n\n"
        "The Emergency Reporting System collects and processes the following data:\n"
        "• Your Telegram ID to identify you\n"
        "• Your language preference\n"
        "• Incident reports you submit (including location)\n"
        "• Voice notes (if you choose to record them)\n\n"
        "This data is used only to:\n"
        "• Provide emergency reporting services\n"
        "• Connect you with appropriate support agencies\n"
        "• Improve the service based on aggregated statistics\n\n"
        "You have the right to:\n"
        "• Access your data\n"
        "• Request deletion of your data\n"
        "• Withdraw consent at any time\n\n"
        "To withdraw consent or request data deletion, use the /privacy_delete command."
    )
    
    await update.message.reply_html(privacy_text)

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Open the report incident page directly."""
    user = update.effective_user
    
    # Ensure user exists and has given consent
    user_profile, is_new_user = await get_or_create_user(
        user.id, 
        first_name=user.first_name
    )
    
    if is_new_user or not user_profile.data_consent:
        return await welcome_new_user(update, context)
    
    keyboard = [
        [InlineKeyboardButton(
            "📝 Report Incident", 
            web_app=WebAppInfo(url=get_report_url(user.id))
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Please click the button below to report an incident:\n\n"
        "• Report Incident - to file a detailed report",
        reply_markup=reply_markup
    )

async def agencies_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Open the find agencies page directly."""
    user = update.effective_user
    
    # Ensure user exists and has given consent
    user_profile, is_new_user = await get_or_create_user(
        user.id, 
        first_name=user.first_name
    )
    
    if is_new_user or not user_profile.data_consent:
        return await welcome_new_user(update, context)
    
    keyboard = [
        [InlineKeyboardButton(
            "🔍 Find Support Agencies", 
            web_app=WebAppInfo(url=AGENCIES_URL)
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Please click the button below to find support agencies near you:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular messages."""
    user = update.effective_user
    message_text = update.message.text.lower()
    
    # Check if message contains keywords related to emergencies or help
    emergency_keywords = ["emergency", "help", "danger", "assault", "attack", "rape", "violence", "hurt", "injured", "accident"]
    help_keywords = ["how", "guide", "instructions", "use", "explain", "what", "info"]
    
    # Create keyboard with main options
    keyboard = [
        [InlineKeyboardButton("🆘 Report Emergency", callback_data="show_report")],
        [InlineKeyboardButton("🔍 Find Support Services", callback_data="show_agencies")],
        [InlineKeyboardButton("❓ How to Use This Bot", callback_data="show_help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Check if message contains emergency-related keywords
    if any(keyword in message_text for keyword in emergency_keywords):
        await update.message.reply_html(
            f"<b>Do you need to report an emergency?</b>\n\n"
            f"If you're in immediate danger, please contact local emergency services directly.\n\n"
            f"You can use this bot to report an incident or find support services:",
            reply_markup=reply_markup
        )
    # Check if message contains help-related keywords
    elif any(keyword in message_text for keyword in help_keywords):
        await update.message.reply_html(
            f"Hi {user.first_name}, I can help you with the following:",
            reply_markup=reply_markup
        )
    # Default response
    else:
        await update.message.reply_html(
            f"Hi {user.first_name}! To use the Emergency Reporting Bot, please use one of the commands below or tap a button:\n\n"
            f"/start - Open the main menu\n"
            f"/help - View instructions on how to use this bot\n"
            f"/report - Report an emergency incident\n"
            f"/agencies - Find support services near you",
            reply_markup=reply_markup
        )

async def show_help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help information when the help button is clicked."""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    user_language = await get_user_language_async(user.id)
    
    help_text = get_text('help_text', user_language)
    
    # Add a button to go back to main menu with translated text
    back_text = get_text('back_to_menu', user_language)
    keyboard = [[InlineKeyboardButton(f"◀️ {back_text}", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=help_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def show_report_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show report incident options when the report button is clicked."""
    query = update.callback_query
    await query.answer()
    user = query.from_user
    
    # Ensure user exists and has given consent
    user_profile, is_new_user = await get_or_create_user(
        user.id, 
        first_name=user.first_name
    )
    
    if is_new_user or not user_profile.data_consent:
        # Create keyboard for language selection
        keyboard = [
            [
                InlineKeyboardButton("English 🇬🇧", callback_data="setlang_en"),
                InlineKeyboardButton("አማርኛ 🇪🇹", callback_data="setlang_am")
            ],
            [
                InlineKeyboardButton("Afaan Oromo 🇪🇹", callback_data="setlang_om")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "<b>Welcome to the Emergency Reporting Bot!</b>\n\n"
            "Before you can report an incident, please select your preferred language:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    else:
        # Create keyboard with WebApp button only
        keyboard = [
            [InlineKeyboardButton(
                "📝 Report Incident", 
                web_app=WebAppInfo(url=get_report_url(user.id))
            )],
            [InlineKeyboardButton("◀️ Back to Main Menu", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "<b>Report an Emergency Incident</b>\n\n"
            "Tap <b>Report Incident</b> to open the reporting form.\n\n"
            "The report form allows you to select the incident type, share your location, "
            "provide details, and record a voice note if needed.",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

async def show_agencies_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show find agencies options when the agencies button is clicked."""
    query = update.callback_query
    await query.answer()
    user = query.from_user
    
    # Ensure user exists and has given consent
    user_profile, is_new_user = await get_or_create_user(
        user.id, 
        first_name=user.first_name
    )
    
    if is_new_user or not user_profile.data_consent:
        # Create keyboard for language selection
        keyboard = [
            [
                InlineKeyboardButton("English 🇬🇧", callback_data="setlang_en"),
                InlineKeyboardButton("አማርኛ 🇪🇹", callback_data="setlang_am")
            ],
            [
                InlineKeyboardButton("Afaan Oromo 🇪🇹", callback_data="setlang_om")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "<b>Welcome to the Emergency Reporting Bot!</b>\n\n"
            "Before you can find support agencies, please select your preferred language:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    else:
        # Create keyboard with WebApp button
        keyboard = [
            [InlineKeyboardButton(
                "🔍 Find Support Agencies", 
                web_app=WebAppInfo(url=AGENCIES_URL)
            )],
            [InlineKeyboardButton("◀️ Back to Main Menu", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "<b>Find Support Agencies Near You</b>\n\n"
            "Tap the button below to find support agencies. You can:\n\n"
            "• Use your current location to find nearby services\n"
            "• Search by region, zone, woreda, and kebele\n"
            "• Filter by service type (police, hospital, etc.)\n"
            "• Get contact information and directions\n\n"
            "This will help you find the closest support services.",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

async def show_safety_info_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show safety information when the safety info button is clicked."""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    language = await get_user_language_async(user.id)
    
    # Add a button to go back to main menu
    keyboard = [[InlineKeyboardButton("◀️ Back to Main Menu", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"<b>🛡️ {get_text('safety_info', language)}</b>\n\n"
        f"{get_text('bot_safety_info', language)}",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def create_application():
    """Create and configure the Application instance."""
    try:
        # Log the bot token for debugging (just the first 5 chars)
        logger.info(f"Creating application with bot token: {BOT_TOKEN[:5]}...")
        
        # Create application with increased timeout
        application = (
            Application.builder()
            .token(BOT_TOKEN)
            .connect_timeout(30.0)  # Increase connection timeout
            .read_timeout(30.0)     # Increase read timeout
            .write_timeout(30.0)    # Increase write timeout
            .build()
        )
        
        # Add a simple test handler for debugging
        async def debug_echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            """Echo the user message for debugging."""
            logger.info(f"Received message: {update.message.text}")
            await update.message.reply_text(f"You said: {update.message.text}")
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("test", test))  # Simple test command
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("report", report_command))
        application.add_handler(CommandHandler("agencies", agencies_command))
        application.add_handler(CommandHandler("language", language_selection_command))  # Use the language bridge command
        application.add_handler(CommandHandler("privacy", privacy_command))
        application.add_handler(CommandHandler("debug", debug_echo))  # Debug command
        
        # Add callback query handlers
        application.add_handler(CallbackQueryHandler(language_button_callback, pattern=r"^setlang_"))  # Use the language bridge callback
        application.add_handler(CallbackQueryHandler(language_button_callback, pattern=r"^lang_"))  # Also handle lang_ pattern
        application.add_handler(CallbackQueryHandler(handle_consent_response, pattern=r"^consent_"))
        application.add_handler(CallbackQueryHandler(change_language, pattern=r"^change_language$"))
        application.add_handler(CallbackQueryHandler(back_to_main, pattern=r"^back_to_main$"))
        application.add_handler(CallbackQueryHandler(show_help_callback, pattern=r"^show_help$"))
        application.add_handler(CallbackQueryHandler(show_report_callback, pattern=r"^show_report$"))
        application.add_handler(CallbackQueryHandler(show_agencies_callback, pattern=r"^show_agencies$"))
        application.add_handler(CallbackQueryHandler(emergency_call_options, pattern=r"^emergency_call_options$"))
        application.add_handler(CallbackQueryHandler(show_safety_info_callback, pattern=r"^show_safety_info$"))
        
        # Add emergency number callback handlers
        application.add_handler(CallbackQueryHandler(handle_emergency_call, pattern=r"^call_\d+$"))
        
        # Handle regular messages
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Log errors
        application.add_error_handler(error_handler)
        
        logger.info("Application created successfully")
        return application
    except Exception as e:
        logger.error(f"Error creating application: {e}", exc_info=True)
        raise

def run_bot():
    """Run the bot in polling mode (used by management command)."""
    try:
        app = create_application()
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Error running bot in polling mode: {e}")
        raise 