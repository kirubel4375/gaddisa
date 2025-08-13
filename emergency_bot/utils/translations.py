from django.utils.translation import gettext as _
from emergency_bot.accounts.models import UserProfile

# Dictionary of translations for each supported language
TRANSLATIONS = {
    'en': {
        'welcome_message': "Welcome! I can help you report emergencies and find assistance.",
        'language_changed': "Language changed to English.",
        'choose_language': "Please choose your preferred language:",
        'choose_service': "Please choose one of the following services:",
        'hospital': "Hospital",
        'police': "Police",
        'ambulance': "Ambulance",
        'women_child_affair': "Women and Child Affairs",
        'invalid_choice': "Invalid choice. Please select again.",
        'no_service_found': "Sorry, no {service} found nearby.",
        'nearby_service': "Here is a nearby {service}:",
        'name': "Name",
        'phone': "Phone",
        'description': "Description",
        'location': "Location",
        'operation_cancelled': "Operation cancelled. Type /start to begin again.",
        'language_button': "Change Language 🌐",
        'report_emergency': "Report Emergency 🚨",
        'find_services': "Find Services 🏥",
        'help_message': "Use /start to begin, /language to change language, or /help to see this message.",
        'cancel': "Cancel",
        'available_services': "Available Services",
        'emergency_numbers': "Emergency Numbers",
        'call_7711_text': "Call 7711 - Emergency Services",
        'call_999_text': "Call 999 - Police",
        'call_907_text': "Call 907 - Ambulance",
        'call_939_text': "Call 939 - Fire Department",
        'call_911_text': "Call 911 - General Emergency",
        'back_to_menu': "Back to Main Menu",
        'emergency_numbers_menu': "<b>📞 Emergency Numbers</b>\n\nChoose an emergency service to call:\n\n🚨 <b>7711</b> - Main Emergency Services\n👮 <b>999</b> - Police Department\n🚑 <b>907</b> - Ambulance Service\n🔥 <b>939</b> - Fire Department\n🏥 <b>911</b> - General Emergency\n\n<i>Tap a number to call directly</i>",
        'how_to_use_bot': "How to use bot",
        'help_text': "<b>📱 Emergency Bot Help</b>\n\n<b>Quick Actions:</b>\n• Emergency Help: Report incidents & get help\n• Find Services: Locate nearby police, hospitals & support\n• Emergency Numbers: Call 7711, 999, 907, 939, 911\n\n<b>Commands:</b>\n/start - Main menu\n/language - Change language\n/help - This help",
        'bot_safety_info': "This bot is designed with your safety and privacy in mind. All your data is encrypted and stored securely. Your location is only used when you explicitly share it. You can delete your data at any time by using the /privacy command. In case of emergency, you can quickly access help by calling 7711 directly from this bot.",
        'safety_info': "Safety Information",
    },
    'am': {
        'welcome_message': "እንኳን ደህና መጡ! አደጋዎችን ሪፖርት ማድረግ እና እርዳታ ማግኘት እችላለሁ።",
        'language_changed': "ቋንቋ ወደ አማርኛ ተቀይሯል።",
        'choose_language': "እባክዎ የሚፈልጉትን ቋንቋ ይምረጡ:",
        'choose_service': "እባክዎ ከሚከተሉት አገልግሎቶች አንዱን ይምረጡ:",
        'hospital': "ሆስፒታል",
        'police': "ፖሊስ",
        'ambulance': "አምቡላንስ",
        'women_child_affair': "የሴቶችና ህጻናት ጉዳይ",
        'invalid_choice': "ልክ ያልሆነ ምርጫ። እባክዎ እንደገና ይምረጡ።",
        'no_service_found': "ይቅርታ፣ በአቅራቢያ {service} አልተገኘም።",
        'nearby_service': "በአቅራቢያ ያለ {service}:",
        'name': "ስም",
        'phone': "ስልክ",
        'description': "መግለጫ",
        'location': "አድራሻ",
        'operation_cancelled': "ክንውኑ ተሰርዟል። እንደገና ለመጀመር /start ይጠቀሙ።",
        'language_button': "ቋንቋ ይቀይሩ 🌐",
        'report_emergency': "አደጋ ሪፖርት ያድርጉ 🚨",
        'find_services': "አገልግሎቶችን ያግኙ 🏥",
        'help_message': "ለመጀመር /start፣ ቋንቋን ለመቀየር /language፣ ወይም ይህን መልእክት ለማየት /help ይጠቀሙ።",
        'cancel': "ሰርዝ",
        'available_services': "የሚገኙ አገልግሎቶች",
        'emergency_numbers': "የአደጋ ጊዜ ቁጥሮች",
        'call_7711_text': "7711 ይደውሉ - የአደጋ ጊዜ አገልግሎቶች",
        'call_999_text': "999 ይደውሉ - ፖሊስ",
        'call_907_text': "907 ይደውሉ - አምቡላንስ",
        'call_939_text': "939 ይደውሉ - እሳት አደጋ መከላከያ",
        'call_911_text': "911 ይደውሉ - አጠቃላይ አደጋ",
        'back_to_menu': "ወደ ዋናው ዝርዝር ይመለሱ",
        'emergency_numbers_menu': "<b>📞 የአደጋ ጊዜ ቁጥሮች</b>\n\nሊደውሉበት የሚፈልጉትን የአደጋ ጊዜ አገልግሎት ይምረጡ:\n\n🚨 <b>7711</b> - ዋና የአደጋ ጊዜ አገልግሎቶች\n👮 <b>999</b> - የፖሊስ መምሪያ\n🚑 <b>907</b> - የአምቡላንስ አገልግሎት\n🔥 <b>939</b> - የእሳት አደጋ መከላከያ መምሪያ\n🏥 <b>911</b> - አጠቃላይ አደጋ\n\n<i>በቀጥታ ለመደወል ቁጥሩን ይንኩ</i>",
        'how_to_use_bot': "ቦቱን እንዴት መጠቀም እንደሚቻል",
        'help_text': "<b>📱 የአደጋ ጊዜ ቦት እርዳታ</b>\n\n<b>ፈጣን እርምጃዎች:</b>\n• የአደጋ ጊዜ እርዳታ: ሪፖርት ያድርጉ እና እርዳታ ያግኙ\n• አገልግሎቶችን ያግኙ: አቅራቢያ ያሉ ፖሊስ፣ ሆስፒታል እና ድጋፍ\n• የአደጋ ጊዜ ቁጥሮች: 7711፣ 999፣ 907፣ 939፣ 911 ይደውሉ\n\n<b>ትዕዛዞች:</b>\n/start - ዋና ዝርዝር\n/language - ቋንቋ ይቀይሩ\n/help - ይህ እርዳታ",
        'bot_safety_info': "ይህ ቦት ለእርስዎ ደህንነት እና ግላዊነት ሲባል የተነደፈ ነው። ሁሉም የእርስዎ ዳታ የተመሰጠረ እና በደህንነት የተከማቸ ነው። የእርስዎ አካባቢ የሚጠቀመው እርስዎ በግልጽ ሲያካፍሉት ብቻ ነው። ዳታዎን በማንኛውም ጊዜ በ/privacy ትዕዛዝ በመጠቀም መሰረዝ ይችላሉ። በአደጋ ጊዜ፣ ከዚህ ቦት በቀጥታ 7711 በመደወል በፍጥነት እርዳታ ማግኘት ይችላሉ።",
        'safety_info': "የደህንነት መረጃ",
    },
    'om': {
        'welcome_message': "Baga nagaan dhufte! Yeroo muddaa gabaasuu fi gargaarsa argachuu nan danda'a.",
        'language_changed': "Afaan gara Afaan Oromootti jijjirame.",
        'choose_language': "Maaloo afaan barbaaddu filaa:",
        'choose_service': "Maaloo tajaajila armaan gadii keessaa tokko filaa:",
        'hospital': "Hospitaala",
        'police': "Poolisii",
        'ambulance': "Ambulaansii",
        'women_child_affair': "Dhimma Dubartootaa fi Daa'immanii",
        'invalid_choice': "Filannoon sirrii miti. Maaloo irra deebi'aa filaa.",
        'no_service_found': "Dhiifama, {service} dhihoo hin argamne.",
        'nearby_service': "Kunis {service} dhihoo jiru:",
        'name': "Maqaa",
        'phone': "Bilbila",
        'description': "Ibsa",
        'location': "Iddoo",
        'operation_cancelled': "Hojiin haqameera. Irra deebi'uuf /start quba buusi.",
        'language_button': "Afaan Jijjiiri 🌐",
        'report_emergency': "Muddaa Gabaasi 🚨",
        'find_services': "Tajaajila Barbaadi 🏥",
        'help_message': "Jalqabuuf /start, afaan jijjiiruuf /language, ykn ergaa kana ilaaluuf /help fayyadami.",
        'cancel': "Haqi",
        'available_services': "Tajaajila Argamu",
        'emergency_numbers': "Lakkoofsa Balaa",
        'call_7711_text': "7711 bilbili - Tajaajila Balaa",
        'call_999_text': "999 bilbili - Poolisii",
        'call_907_text': "907 bilbili - Ambulaansii",
        'call_939_text': "939 bilbili - Ibidda Dhaamsuu",
        'call_911_text': "911 bilbili - Balaa Waliigalaa",
        'back_to_menu': "Gara Tarree Jalqabaatti Deebi'i",
        'emergency_numbers_menu': "<b>📞 Lakkoofsa Balaa</b>\n\nTajaajila balaa bilbiluu barbaaddu filaa:\n\n🚨 <b>7711</b> - Tajaajila Balaa Jalqabaa\n👮 <b>999</b> - Muummee Poolisii\n🚑 <b>907</b> - Tajaajila Ambulaansii\n🔥 <b>939</b> - Muummee Ibidda Dhaamsuu\n🏥 <b>911</b> - Balaa Waliigalaa\n\n<i>Kallattiin bilbiluuf lakkoofsa tuqi</i>",
        'how_to_use_bot': "Akkaataa fayyadama bot",
        'help_text': "<b>📱 Gargaarsa Bot Balaa</b>\n\n<b>Gocha Saffisaa:</b>\n• Gargaarsa Balaa: Gabaasa fi gargaarsa argadhu\n• Tajaajila Barbaadi: Poolisii, hospitaala fi deeggarsa dhihoo\n• Lakkoofsa Balaa: 7711, 999, 907, 939, 911 bilbilaa\n\n<b>Ajajawwan:</b>\n/start - Tarree jalqabaa\n/language - Afaan jijjiiri\n/help - Gargaarsa kana",
        'bot_safety_info': "Bot kun nageenya keessan fi iccitii keessan yaada keessa galchuun qophaa'e. Daataan keessan hundi qindaa'ee fi nageenya qabeessaan kuufama. Bakki keessan kan fayyadamu yoo ifatti qoodtan qofa. Daataa keessan yeroo barbaaddan /privacy ajaja fayyadamuun haquu dandeessu. Yeroo muddaa, bot kana irraa kallattiin 7711 bilbiluun dafanii gargaarsa argachuu dandeessu.",
        'safety_info': "Odeeffannoo Nageenyaa",
    }
}

def get_text(key, language_code='en', **kwargs):
    """
    Get translated text for a key in the specified language
    
    Args:
        key: The translation key
        language_code: The language code (en, am, or om)
        **kwargs: Format arguments for the string
    
    Returns:
        The translated text
    """
    if language_code not in TRANSLATIONS:
        language_code = 'en'
    
    translations = TRANSLATIONS[language_code]
    text = translations.get(key, TRANSLATIONS['en'].get(key, key))
    
    if kwargs:
        return text.format(**kwargs)
    
    return text

def get_user_language(telegram_id):
    """
    Get the language preference for a user
    
    Args:
        telegram_id: The Telegram user ID
    
    Returns:
        The language code (en, am, or om)
    """
    try:
        user = UserProfile.objects.get(telegram_id=telegram_id)
        return user.language
    except UserProfile.DoesNotExist:
        # Default to English if user doesn't exist
        return 'en'

def update_user_language(telegram_id, language_code):
    """
    Update the language preference for a user with comprehensive database logging
    
    Args:
        telegram_id: The Telegram user ID
        language_code: The language code (en, am, or om)
    
    Returns:
        True if successful, False otherwise
    """
    import logging
    import sys
    from pathlib import Path
    
    # Setup standard logging
    logger = logging.getLogger(__name__)
    
    # Try to import language debug logging
    try:
        # Add project root to path
        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        from language_debug_logging import get_language_logger, log_database_operation, log_user_language_change
        debug_logger = get_language_logger(__name__)
        use_debug_logging = True
    except ImportError:
        debug_logger = logger
        use_debug_logging = False
        logger.warning("Language debug logging not available, using standard logging")
    
    debug_logger.info(f"update_user_language called with telegram_id={telegram_id}, language_code={language_code}")
    
    try:
        # Make sure telegram_id is a string
        telegram_id = str(telegram_id)
        debug_logger.debug(f"Converted telegram_id to string: {telegram_id}")
        
        # Check if language_code is valid
        valid_languages = ['en', 'am', 'om']
        if language_code not in valid_languages:
            error_msg = f"Invalid language code: {language_code}. Valid codes: {valid_languages}"
            debug_logger.error(error_msg)
            if use_debug_logging:
                log_user_language_change(telegram_id, 'unknown', language_code, success=False, error_msg=error_msg)
            return False
        
        debug_logger.debug(f"Language code {language_code} is valid")
        
        # Log database operation attempt
        if use_debug_logging:
            log_database_operation("GET_OR_CREATE", "UserProfile", telegram_id, ["telegram_id", "language"], success=False)
        
        # Get current user state for comparison
        try:
            existing_user = UserProfile.objects.get(telegram_id=telegram_id)
            old_language = existing_user.language
            user_exists = True
            debug_logger.debug(f"Found existing user {telegram_id} with current language: {old_language}")
        except UserProfile.DoesNotExist:
            old_language = None
            user_exists = False
            debug_logger.debug(f"User {telegram_id} does not exist, will create new profile")
        
        # Get or create user profile
        debug_logger.debug(f"Attempting get_or_create for user {telegram_id}")
        user, created = UserProfile.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={'language': language_code}
        )
        
        if created:
            # Log successful user creation
            if use_debug_logging:
                log_database_operation("CREATE", "UserProfile", telegram_id, ["telegram_id", "language"], success=True)
                log_user_language_change(telegram_id, 'none', language_code, success=True)
            
            debug_logger.info(f"Created new user profile for {telegram_id} with language {language_code}")
            return True
        else:
            # Log successful user retrieval
            if use_debug_logging:
                log_database_operation("GET", "UserProfile", telegram_id, ["telegram_id", "language"], success=True)
            
            # Check if language needs updating
            if user.language == language_code:
                debug_logger.info(f"User {telegram_id} already has language set to {language_code}, no update needed")
                if use_debug_logging:
                    log_user_language_change(telegram_id, old_language, language_code, success=True)
                return True
            
            # Update existing user's language
            debug_logger.info(f"Updating existing user {telegram_id} language from {user.language} to {language_code}")
            
            # Log database update attempt
            if use_debug_logging:
                log_database_operation("UPDATE", "UserProfile", telegram_id, ["language"], success=False)
            
            try:
                old_lang = user.language
                user.language = language_code
                user.save(update_fields=['language'])
                
                # Log successful update
                if use_debug_logging:
                    log_database_operation("UPDATE", "UserProfile", telegram_id, ["language"], success=True)
                    log_user_language_change(telegram_id, old_lang, language_code, success=True)
                
                debug_logger.info(f"Successfully updated language for user {telegram_id} from {old_lang} to {language_code}")
                
                # Verify the update by re-fetching the user
                user.refresh_from_db()
                if user.language == language_code:
                    debug_logger.debug(f"Verified: User {telegram_id} language is now {user.language}")
                    return True
                else:
                    error_msg = f"Verification failed: Expected {language_code}, got {user.language}"
                    debug_logger.error(error_msg)
                    if use_debug_logging:
                        log_database_operation("UPDATE", "UserProfile", telegram_id, ["language"], success=False, error_msg=error_msg)
                        log_user_language_change(telegram_id, old_lang, language_code, success=False, error_msg=error_msg)
                    return False
                    
            except Exception as save_error:
                error_msg = f"Error saving language update: {str(save_error)}"
                debug_logger.error(error_msg, exc_info=True)
                if use_debug_logging:
                    log_database_operation("UPDATE", "UserProfile", telegram_id, ["language"], success=False, error_msg=error_msg)
                    log_user_language_change(telegram_id, old_lang if 'old_lang' in locals() else user.language, language_code, success=False, error_msg=error_msg)
                return False
                
    except Exception as e:
        error_msg = f"Exception in update_user_language: {str(e)}"
        debug_logger.error(f"Error updating language for user {telegram_id}: {e}", exc_info=True)
        
        if use_debug_logging:
            log_database_operation("UPDATE", "UserProfile", telegram_id, ["language"], success=False, error_msg=error_msg)
            log_user_language_change(telegram_id, old_language if 'old_language' in locals() else 'unknown', language_code, success=False, error_msg=error_msg)
        
        import traceback
        debug_logger.error(f"Full traceback: {traceback.format_exc()}")
        return False 