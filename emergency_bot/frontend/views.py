"""
Views for the frontend app (Telegram Mini App).
"""

import json
import logging
import os
import uuid
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from emergency_bot.accounts.models import UserProfile
from emergency_bot.reports.models import IncidentReport
from emergency_bot.agencies.models import Agency

from emergency_bot.accounts.middleware import telegram_auth_required
from django.utils import translation
from django.http import HttpResponseRedirect
from django.utils import timezone

logger = logging.getLogger(__name__)


def get_user_profile(request):
    """Get or create UserProfile from Telegram user ID in query params"""
    telegram_id = request.GET.get('user_id')
    
    if not telegram_id:
        logger.warning("No user_id provided in request")
        return None
    
    try:
        user_profile, created = UserProfile.objects.get_or_create(
            telegram_id=telegram_id
        )
        
        # Update last active time
        user_profile.update_last_active()
        
        # For debugging
        if created:
            logger.info(f"Created new user profile for Telegram ID: {telegram_id}")
        
        # Add user_profile to request for use in other views
        request.user_profile = user_profile
        return user_profile
    
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        return None


def activate_user_language(request, user_profile=None):
    """Activate user's preferred language for the request with localStorage support"""
    if not user_profile:
        user_profile = get_user_profile(request)
    
    # Priority order: URL lang parameter > user profile > default
    # Check for language parameter in URL (from localStorage navigation)
    lang_param = request.GET.get('lang')
    
    if lang_param and lang_param in ['en', 'am', 'om']:
        # Use language from URL parameter (localStorage navigation)
        active_language = lang_param
        # Update user profile to match localStorage preference
        if user_profile:
            user_profile.language = lang_param
            user_profile.save()
            logger.info(f"Updated user {user_profile.telegram_id} language to {lang_param} from localStorage")
    elif user_profile and user_profile.language:
        # Use user's saved language preference from database
        active_language = user_profile.language
    else:
        # Default to English
        active_language = 'en'
        # Set default language for new users
        if user_profile:
            user_profile.language = 'en'
            user_profile.save()
    
    # Activate the language
    translation.activate(active_language)
    request.LANGUAGE_CODE = active_language
    logger.info(f"Activated language: {active_language} for user {user_profile.telegram_id if user_profile else 'anonymous'}")
    
    return active_language


def index(request):
    """
    Main entry point for the Telegram Mini App.
    """
    # Get user profile and activate their preferred language
    user_profile = get_user_profile(request)
    active_language = activate_user_language(request, user_profile)
    
    return render(request, 'index.html')


@telegram_auth_required
def welcome(request):
    """
    Welcome screen for first-time users with onboarding steps.
    """
    # Get user profile and activate their preferred language
    user_profile = get_user_profile(request)
    activate_user_language(request, user_profile)
    
    return render(request, 'welcome.html')


@csrf_exempt
def get_user_language(request):
    """Get user's current language preference."""
    try:
        telegram_id = request.GET.get('user_id')
        if not telegram_id:
            return JsonResponse({'success': False, 'error': 'User ID required'})
        
        try:
            user_profile = UserProfile.objects.get(telegram_id=telegram_id)
            return JsonResponse({'success': True, 'language': user_profile.language})
        except UserProfile.DoesNotExist:
            return JsonResponse({'success': True, 'language': 'en'})
    except Exception as e:
        logger.error(f"Error getting user language: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
def check_language_sync(request):
    """
    Check for language changes since last check (polling endpoint for shared hosting).
    """
    try:
        telegram_id = request.GET.get('user_id')
        last_check = request.GET.get('last_check')  # ISO timestamp
        
        logger.info(f"Language sync check for user {telegram_id}, last_check: {last_check}")
        
        if not telegram_id:
            return JsonResponse({'success': False, 'error': 'User ID required'})
        
        try:
            # Get or create user profile if it doesn't exist
            user_profile, created = UserProfile.objects.get_or_create(
                telegram_id=telegram_id,
                defaults={'language': 'en'}
            )
            
            if created:
                logger.info(f"Created new user profile for telegram_id: {telegram_id}")
            
            current_info = user_profile.get_current_language_info()
            logger.info(f"Current info for user {telegram_id}: {current_info}")
            
            # Check if language changed since last check
            language_changed = False
            if last_check and user_profile.language_changed_at:
                try:
                    from datetime import datetime
                    last_check_time = datetime.fromisoformat(last_check.replace('Z', '+00:00'))
                    language_changed = user_profile.get_language_changes_since(last_check_time)
                    logger.info(f"Language changed since {last_check}: {language_changed}")
                except (ValueError, TypeError) as e:
                    # Invalid timestamp format, assume change occurred
                    logger.warning(f"Invalid timestamp format: {e}")
                    language_changed = True
            elif not last_check:
                # First time checking, don't treat as change
                language_changed = False
                logger.info("First time checking, no change assumed")
            
            response_data = {
                'success': True,
                'language': current_info['language'],
                'changed_at': current_info['changed_at'],
                'timestamp': current_info['timestamp'],
                'language_changed': language_changed
            }
            
            logger.info(f"Returning response: {response_data}")
            return JsonResponse(response_data)
            
        except Exception as db_error:
            logger.error(f"Database error for user {telegram_id}: {db_error}")
            return JsonResponse({
                'success': True,
                'language': 'en',
                'changed_at': None,
                'timestamp': timezone.now().isoformat(),
                'language_changed': False
            })
    except Exception as e:
        logger.error(f"Error checking language sync: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
def save_location(request):
    """Save user's location data."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            telegram_id = data.get('telegram_id')
            
            if not latitude or not longitude or not telegram_id:
                return JsonResponse({'success': False, 'error': 'Missing required fields'})
            
            try:
                user_profile, created = UserProfile.objects.get_or_create(
                    telegram_id=telegram_id
                )
                user_profile.update_location(float(latitude), float(longitude))
                
                return JsonResponse({'success': True, 'message': 'Location saved successfully'})
            except UserProfile.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'User not found'})
        except Exception as e:
            logger.error(f"Error saving location: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
def get_location_status(request):
    """Get user's location permission status and recent location if available."""
    try:
        telegram_id = request.GET.get('user_id')
        if not telegram_id:
            return JsonResponse({'success': False, 'error': 'User ID required'})
        
        try:
            user_profile = UserProfile.objects.get(telegram_id=telegram_id)
            
            response_data = {
                'success': True,
                'needs_permission': user_profile.needs_location_permission(),
                'has_location': bool(user_profile.latitude and user_profile.longitude),
                'location_granted': user_profile.location_permission_granted,
            }
            
            # Include location data if available and recent
            if user_profile.has_recent_location():
                response_data.update({
                    'latitude': user_profile.latitude,
                    'longitude': user_profile.longitude,
                    'location_updated_at': user_profile.location_updated_at.isoformat(),
                })
            
            return JsonResponse(response_data)
        except UserProfile.DoesNotExist:
            return JsonResponse({
                'success': True,
                'needs_permission': True,
                'has_location': False,
                'location_granted': False,
            })
    except Exception as e:
        logger.error(f"Error getting location status: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
def update_language(request):
    """
    Update user's language preference.
    """
    try:
        data = json.loads(request.body)
        language = data.get('language')
        
        if language not in ['en', 'am', 'om']:
            return JsonResponse({'success': False, 'error': 'Invalid language'})
        
        # Get user profile from request or create one
        user_profile = getattr(request, 'user_profile', None)
        if not user_profile:
            # Try to get from request body or query params
            telegram_id = data.get('telegram_id') or request.GET.get('user_id')
            if telegram_id:
                user_profile, created = UserProfile.objects.get_or_create(
                    telegram_id=telegram_id
                )
            else:
                return JsonResponse({'success': False, 'error': 'User profile not found'})
        
        # Update user profile language with sync tracking
        user_profile.update_language_with_sync(language)
        
        # Activate the language for the current session
        translation.activate(language)
        request.LANGUAGE_CODE = language
        
        logger.info(f"Updated language for user {user_profile.telegram_id} to {language}")
        
        return JsonResponse({'success': True, 'language': language})
    except Exception as e:
        logger.error(f"Error updating language: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@telegram_auth_required
@require_POST
@csrf_exempt
def update_consent(request):
    """
    Update user's data consent preference.
    """
    try:
        data = json.loads(request.body)
        consent = data.get('consent', False)
        
        # Update user profile
        user_profile = request.user_profile
        
        if consent:
            user_profile.grant_consent()
        else:
            user_profile.revoke_consent()
        
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Error updating consent: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


def agencies(request):
    """
    View for agencies listing and search.
    """
    # Get user profile and activate their preferred language
    user_profile = get_user_profile(request)
    activate_user_language(request, user_profile)
    
    return render(request, 'agencies.html')


def agency_detail_page(request):
    """
    View for displaying individual agency details page.
    """
    # Simple view that just renders the template
    return render(request, 'agency-detail.html')


def report(request):
    """
    View for incident reporting.
    """
    # Get user profile and activate their preferred language
    user_profile = get_user_profile(request)
    activate_user_language(request, user_profile)
    
    return render(request, 'report.html')


@csrf_exempt
def submit_report(request):
    """
    API endpoint for submitting incident reports.
    """
    if request.method == 'POST':
        try:
            # Parse JSON data from request body
            data = json.loads(request.body)
            
            # Extract required fields
            incident_type = data.get('incident_type')
            description = data.get('description', '')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            voice_note_url = data.get('voice_note_url', '')
            telegram_id = data.get('telegram_id')
            
            # Validate required fields
            if not incident_type:
                return JsonResponse({'status': 'error', 'message': 'Incident type is required'}, status=400)
            
            if not latitude or not longitude:
                return JsonResponse({'status': 'error', 'message': 'Location is required'}, status=400)
            
            if not telegram_id:
                return JsonResponse({'status': 'error', 'message': 'User ID is required'}, status=400)
            
            # Get or create user profile
            try:
                user_profile, created = UserProfile.objects.get_or_create(
                    telegram_id=telegram_id
                )
            except Exception as e:
                logger.error(f"Error getting/creating user profile: {e}")
                return JsonResponse({'status': 'error', 'message': 'Invalid user ID'}, status=400)
            
            # Create and save the incident report
            try:
                # Skip encryption to avoid Fernet key error
                report = IncidentReport(
                    user=user_profile,
                    type=incident_type,
                    description=description,  # Store as plaintext for now
                    voice_note_url=voice_note_url,
                    location=f"GPS: {latitude}, {longitude}",
                    latitude=latitude,
                    longitude=longitude
                )
                
                # Skip the automatic encryption in save() method
                report.save()
                
                logger.info(f"New incident report created: {report.id} by user {telegram_id}")
                
                return JsonResponse({
                    'status': 'success', 
                    'message': 'Report submitted successfully',
                    'report_id': str(report.id)  # Convert UUID to string
                })
            
            except Exception as e:
                logger.error(f"Error creating incident report: {e}")
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
                
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.error(f"Error processing report submission: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def upload_voice_note(request):
    """
    API endpoint for uploading voice notes.
    """
    if request.method == 'POST':
        try:
            # Check if the voice note is in the request
            if 'voice_note' not in request.FILES:
                return JsonResponse({'status': 'error', 'message': 'No voice note provided'}, status=400)
            
            voice_note = request.FILES['voice_note']
            
            # Generate a unique filename with UUID to prevent collisions
            unique_id = str(uuid.uuid4())
            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'voice_notes/{unique_id}/{date_str}.wav'
            
            # Ensure directory exists
            directory = os.path.dirname(os.path.join(settings.MEDIA_ROOT, filename))
            os.makedirs(directory, exist_ok=True)
            
            # Save the file to media storage
            path = default_storage.save(filename, ContentFile(voice_note.read()))
            
            # Generate the URL for the saved file
            voice_note_url = settings.MEDIA_URL + path
            
            # Return the URL of the saved file
            return JsonResponse({
                'status': 'success',
                'message': 'Voice note uploaded successfully',
                'voice_note_url': voice_note_url
            })
            
        except Exception as e:
            logger.error(f"Error uploading voice note: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


def profile(request):
    """
    View for user profile management.
    """
    # Get user profile and activate their preferred language
    user_profile = get_user_profile(request)
    activate_user_language(request, user_profile)
    
    return render(request, 'profile.html')


@telegram_auth_required
def report_history(request):
    """
    View for user's report history.
    """
    # Get user profile and activate their preferred language
    user_profile = get_user_profile(request)
    activate_user_language(request, user_profile)
    
    return render(request, 'reports.html')


def agency_detail(request, slug):
    """
    View for individual agency details.
    """
    # Get user profile and activate their preferred language
    user_profile = get_user_profile(request)
    activate_user_language(request, user_profile)
    
    agency = get_object_or_404(Agency, slug=slug)
    return render(request, 'agency_detail.html', {'agency': agency})


def my_reports(request):
    """
    View for user's own reports.
    """
    # Get user profile and activate their preferred language
    user_profile = get_user_profile(request)
    activate_user_language(request, user_profile)
    
    return render(request, 'my_reports.html')


def report_detail(request, report_id):
    """
    View for individual report details.
    """
    # Get user profile and activate their preferred language
    user_profile = get_user_profile(request)
    activate_user_language(request, user_profile)
    
    report = get_object_or_404(IncidentReport, id=report_id)
    return render(request, 'report_detail.html', {'report': report}) 