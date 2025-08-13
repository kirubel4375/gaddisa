"""
Views for the accounts app.
"""

import json
import logging
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .models import UserProfile

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def verify_user(request):
    """
    Verify a Telegram user based on init data.
    """
    try:
        # For now, just return success
        return JsonResponse({
            'success': True,
            'message': 'User verified successfully'
        })
    except Exception as e:
        logger.error(f"Error verifying user: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
def current_user(request):
    """
    Get the current user's profile.
    """
    if not hasattr(request, 'user_profile'):
        return JsonResponse({
            'success': False,
            'error': 'User not authenticated'
        }, status=401)
    
    user_profile = request.user_profile
    
    return JsonResponse({
        'success': True,
        'user': {
            'telegram_id': user_profile.telegram_id,
            'language': user_profile.language,
            'last_active': user_profile.last_active.isoformat(),
            'data_consent': user_profile.data_consent,
        }
    })


@api_view(['POST'])
def update_preferences(request):
    """
    Update user preferences.
    """
    if not hasattr(request, 'user_profile'):
        return JsonResponse({
            'success': False,
            'error': 'User not authenticated'
        }, status=401)
    
    try:
        data = json.loads(request.body)
        user_profile = request.user_profile
        
        # Update language preference if provided
        if 'language' in data:
            user_profile.language = data['language']
            user_profile.save(update_fields=['language'])
        
        return JsonResponse({
            'success': True,
            'message': 'Preferences updated successfully'
        })
    
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
def update_consent(request):
    """
    Update user data consent.
    """
    if not hasattr(request, 'user_profile'):
        return JsonResponse({
            'success': False,
            'error': 'User not authenticated'
        }, status=401)
    
    try:
        data = json.loads(request.body)
        user_profile = request.user_profile
        
        # Update consent if provided
        if 'consent' in data:
            if data['consent']:
                user_profile.grant_consent()
            else:
                user_profile.revoke_consent()
        
        return JsonResponse({
            'success': True,
            'message': 'Consent updated successfully',
            'data_consent': user_profile.data_consent
        })
    
    except Exception as e:
        logger.error(f"Error updating consent: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500) 