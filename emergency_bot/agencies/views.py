"""
Views for the agencies app.
"""

import json
import logging
import math
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import F, ExpressionWrapper, FloatField
from django.contrib.auth.decorators import login_required

from emergency_bot.accounts.middleware import telegram_auth_required
from .models import Agency

logger = logging.getLogger(__name__)

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the Haversine distance between two points in kilometers.
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of Earth in kilometers
    
    return c * r

@telegram_auth_required
@require_GET
def nearby_agencies(request):
    """
    API endpoint to get nearby agencies based on latitude and longitude.
    """
    try:
        # Get coordinates from query parameters
        latitude = request.GET.get('lat')
        longitude = request.GET.get('lng')
        
        if not latitude or not longitude:
            return JsonResponse({'error': 'Missing latitude or longitude'}, status=400)
        
        # Convert to float
        lat = float(latitude)
        lng = float(longitude)
        
        # Get all agencies
        agencies = Agency.objects.all()
        
        # Calculate distance for each agency
        result = []
        for agency in agencies:
            distance = calculate_distance(lat, lng, agency.latitude, agency.longitude)
            
            # Only include agencies within 50km
            if distance <= 50:
                result.append({
                    'id': agency.id,
                    'name': agency.name,
                    'type': agency.type,
                    'address': agency.address,
                    'phone': agency.phone,
                    'services': agency.services,
                    'latitude': agency.latitude,
                    'longitude': agency.longitude,
                    'distance': round(distance, 2)  # Round to 2 decimal places
                })
        
        # Sort by distance
        result.sort(key=lambda x: x['distance'])
        
        return JsonResponse(result, safe=False)
    
    except Exception as e:
        logger.error(f"Error finding nearby agencies: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@telegram_auth_required
@require_GET
def search_agencies(request):
    """
    API endpoint to search agencies by region, zone, woreda, kebele.
    """
    try:
        # Get filter parameters
        region = request.GET.get('region')
        zone = request.GET.get('zone')
        woreda = request.GET.get('woreda')
        kebele = request.GET.get('kebele')
        
        # Start with all agencies
        agencies = Agency.objects.all()
        
        # Apply filters if provided
        if region:
            agencies = agencies.filter(region=region)
        if zone:
            agencies = agencies.filter(zone=zone)
        if woreda:
            agencies = agencies.filter(woreda=woreda)
        if kebele:
            agencies = agencies.filter(kebele=kebele)
        
        # Convert to list of dictionaries
        result = []
        for agency in agencies:
            result.append({
                'id': agency.id,
                'name': agency.name,
                'type': agency.type,
                'address': agency.address,
                'phone': agency.phone,
                'services': agency.services,
                'latitude': agency.latitude,
                'longitude': agency.longitude,
                'region': agency.region,
                'zone': agency.zone,
                'woreda': agency.woreda,
                'kebele': agency.kebele
            })
        
        return JsonResponse(result, safe=False)
    
    except Exception as e:
        logger.error(f"Error searching agencies: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@telegram_auth_required
@require_GET
def get_zones(request):
    """
    API endpoint to get zones for a given region.
    """
    try:
        region = request.GET.get('region')
        
        if not region:
            return JsonResponse({'error': 'Missing region parameter'}, status=400)
        
        zones = Agency.objects.filter(region=region).values_list('zone', flat=True).distinct()
        
        return JsonResponse(list(zones), safe=False)
    
    except Exception as e:
        logger.error(f"Error getting zones: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@telegram_auth_required
@require_GET
def get_woredas(request):
    """
    API endpoint to get woredas for a given region and zone.
    """
    try:
        region = request.GET.get('region')
        zone = request.GET.get('zone')
        
        if not region or not zone:
            return JsonResponse({'error': 'Missing region or zone parameter'}, status=400)
        
        woredas = Agency.objects.filter(region=region, zone=zone).values_list('woreda', flat=True).distinct()
        
        return JsonResponse(list(woredas), safe=False)
    
    except Exception as e:
        logger.error(f"Error getting woredas: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@telegram_auth_required
@require_GET
def get_kebeles(request):
    """
    API endpoint to get kebeles for a given region, zone, and woreda.
    """
    try:
        region = request.GET.get('region')
        zone = request.GET.get('zone')
        woreda = request.GET.get('woreda')
        
        if not region or not zone or not woreda:
            return JsonResponse({'error': 'Missing region, zone, or woreda parameter'}, status=400)
        
        kebeles = Agency.objects.filter(region=region, zone=zone, woreda=woreda).values_list('kebele', flat=True).distinct()
        
        return JsonResponse(list(kebeles), safe=False)
    
    except Exception as e:
        logger.error(f"Error getting kebeles: {e}")
        return JsonResponse({'error': str(e)}, status=500) 