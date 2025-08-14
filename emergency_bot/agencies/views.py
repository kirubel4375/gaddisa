"""
Views for the agencies app.
"""

import json
import logging
import math
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import F, ExpressionWrapper, FloatField
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.conf import settings

from emergency_bot.accounts.middleware import telegram_auth_required
from .models import Agency

logger = logging.getLogger(__name__)

# Fallback agencies data for when database is empty and internet is unavailable
FALLBACK_AGENCIES = [
    {
        'id': '1',
        'name': 'Bole Police Station',
        'type': 'police',
        'description': 'Main police station in Bole area with 24/7 service',
        'region': 'Addis Ababa',
        'zone': 'Bole',
        'woreda': '01',
        'kebele': '01',
        'phone': '+251114670001',
        'address': 'Bole Road, near Edna Mall, Addis Ababa',
        'latitude': 8.9936,
        'longitude': 38.7870,
        'hours_of_operation': '24/7',
        'services': 'Emergency response, Crime reporting, Traffic issues',
        'verified': True,
        'active': True
    },
    {
        'id': '2',
        'name': 'Black Lion Hospital',
        'type': 'hospital',
        'description': 'Major referral hospital with emergency services',
        'region': 'Addis Ababa',
        'zone': 'Kirkos',
        'woreda': '04',
        'kebele': '05',
        'phone': '+251115517011',
        'address': 'Zambia St, Addis Ababa',
        'latitude': 9.0107,
        'longitude': 38.7476,
        'hours_of_operation': '24/7 Emergency',
        'services': 'Emergency care, General medicine, Surgery',
        'verified': True,
        'active': True
    },
    {
        'id': '3',
        'name': 'Ethiopian Women Lawyers Association',
        'type': 'ngo',
        'description': 'Legal aid and support for women and children',
        'region': 'Addis Ababa',
        'zone': 'Kirkos',
        'woreda': '02',
        'kebele': '03',
        'phone': '+251115505050',
        'address': 'Kirkos, Addis Ababa',
        'latitude': 9.0145,
        'longitude': 38.7632,
        'hours_of_operation': 'Mon-Fri 8:00-17:00',
        'services': 'Legal consultation, Women rights advocacy',
        'verified': True,
        'active': True
    }
]

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

def get_agencies_from_database():
    """
    Get agencies from database with error handling.
    Returns tuple: (agencies_list, source)
    """
    try:
        agencies = Agency.objects.filter(active=True)
        if agencies.exists():
            result = []
            for agency in agencies:
                result.append({
                    'id': str(agency.id),
                    'name': agency.name,
                    'type': agency.type,
                    'description': agency.description,
                    'region': agency.region,
                    'zone': agency.zone,
                    'woreda': agency.woreda,
                    'kebele': agency.kebele,
                    'phone': agency.phone,
                    'alt_phone': agency.alt_phone,
                    'email': agency.email,
                    'address': agency.address,
                    'latitude': float(agency.latitude),
                    'longitude': float(agency.longitude),
                    'hours_of_operation': agency.hours_of_operation,
                    'services': agency.services,
                    'verified': agency.verified,
                    'active': agency.active
                })
            logger.info(f"Loaded {len(result)} agencies from database")
            return result, 'database'
        else:
            logger.warning("No agencies found in database")
            return [], 'database_empty'
    except Exception as e:
        logger.error(f"Database error: {e}")
        return [], 'database_error'

def get_agencies_from_internet():
    """
    Fetch agencies from external API with caching.
    Returns tuple: (agencies_list, source)
    """
    try:
        # Check cache first
        cached_agencies = cache.get('external_agencies')
        if cached_agencies:
            logger.info(f"Loaded {len(cached_agencies)} agencies from cache")
            return cached_agencies, 'internet_cached'
        
        # Try to fetch from external API (placeholder URL)
        external_api_url = getattr(settings, 'EXTERNAL_AGENCIES_API_URL', None)
        if external_api_url:
            response = requests.get(external_api_url, timeout=10)
            if response.status_code == 200:
                agencies_data = response.json()
                # Cache for 1 hour
                cache.set('external_agencies', agencies_data, 3600)
                logger.info(f"Loaded {len(agencies_data)} agencies from external API")
                return agencies_data, 'internet'
            else:
                logger.warning(f"External API returned status {response.status_code}")
        else:
            logger.info("No external API URL configured")
        
        return [], 'internet_unavailable'
    except requests.RequestException as e:
        logger.warning(f"Internet request failed: {e}")
        return [], 'internet_error'
    except Exception as e:
        logger.error(f"Unexpected error fetching from internet: {e}")
        return [], 'internet_error'

def get_agencies_with_fallback():
    """
    Get agencies with comprehensive fallback strategy:
    1. Try database first
    2. If database empty/error, try internet
    3. If internet fails, use hard-coded fallback
    Returns tuple: (agencies_list, source)
    """
    # Step 1: Try database
    agencies, source = get_agencies_from_database()
    if agencies:
        return agencies, source
    
    logger.info("Database unavailable or empty, trying internet fallback")
    
    # Step 2: Try internet
    agencies, source = get_agencies_from_internet()
    if agencies:
        return agencies, source
    
    logger.info("Internet unavailable, using hard-coded fallback")
    
    # Step 3: Use hard-coded fallback
    return FALLBACK_AGENCIES, 'fallback'

@telegram_auth_required
@require_GET
def nearby_agencies(request):
    """
    API endpoint to get nearby agencies based on latitude and longitude.
    Uses database-first approach with internet and hard-coded fallbacks.
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
        
        # Get agencies with fallback strategy
        agencies, source = get_agencies_with_fallback()
        
        # Calculate distance for each agency
        result = []
        for agency in agencies:
            try:
                agency_lat = float(agency['latitude'])
                agency_lng = float(agency['longitude'])
                distance = calculate_distance(lat, lng, agency_lat, agency_lng)
                
                # Only include agencies within 50km
                if distance <= 50:
                    agency_data = agency.copy()
                    agency_data['distance'] = round(distance, 2)
                    result.append(agency_data)
            except (ValueError, KeyError) as e:
                logger.warning(f"Skipping agency due to invalid coordinates: {e}")
                continue
        
        # Sort by distance
        result.sort(key=lambda x: x.get('distance', float('inf')))
        
        # Add metadata about data source
        response_data = {
            'agencies': result,
            'source': source,
            'count': len(result)
        }
        
        logger.info(f"Returned {len(result)} nearby agencies from {source}")
        return JsonResponse(response_data, safe=False)
    
    except Exception as e:
        logger.error(f"Error finding nearby agencies: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@telegram_auth_required
@require_GET
def search_agencies(request):
    """
    API endpoint to search agencies by region, zone, woreda, kebele.
    Uses database-first approach with fallback.
    """
    try:
        # Get filter parameters
        region = request.GET.get('region')
        zone = request.GET.get('zone')
        woreda = request.GET.get('woreda')
        kebele = request.GET.get('kebele')
        
        # Get agencies with fallback strategy
        agencies, source = get_agencies_with_fallback()
        
        # Apply filters if provided
        filtered_agencies = agencies
        
        if region:
            filtered_agencies = [a for a in filtered_agencies if a.get('region', '').lower() == region.lower()]
        if zone:
            filtered_agencies = [a for a in filtered_agencies if a.get('zone', '').lower() == zone.lower()]
        if woreda:
            filtered_agencies = [a for a in filtered_agencies if a.get('woreda', '') == woreda]
        if kebele:
            filtered_agencies = [a for a in filtered_agencies if a.get('kebele', '') == kebele]
        
        # Add metadata about data source
        response_data = {
            'agencies': filtered_agencies,
            'source': source,
            'count': len(filtered_agencies),
            'filters': {
                'region': region,
                'zone': zone,
                'woreda': woreda,
                'kebele': kebele
            }
        }
        
        logger.info(f"Returned {len(filtered_agencies)} filtered agencies from {source}")
        return JsonResponse(response_data, safe=False)
    
    except Exception as e:
        logger.error(f"Error searching agencies: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@telegram_auth_required
@require_GET
def get_zones(request):
    """
    API endpoint to get zones for a given region.
    Uses database-first approach with fallback.
    """
    try:
        region = request.GET.get('region')
        
        if not region:
            return JsonResponse({'error': 'Missing region parameter'}, status=400)
        
        # Get agencies with fallback strategy
        agencies, source = get_agencies_with_fallback()
        
        # Extract unique zones for the given region
        zones = list(set(
            agency.get('zone', '') for agency in agencies 
            if agency.get('region', '').lower() == region.lower() and agency.get('zone')
        ))
        zones.sort()
        
        response_data = {
            'zones': zones,
            'source': source,
            'region': region
        }
        
        logger.info(f"Returned {len(zones)} zones for region '{region}' from {source}")
        return JsonResponse(response_data, safe=False)
    
    except Exception as e:
        logger.error(f"Error getting zones: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@telegram_auth_required
@require_GET
def get_woredas(request):
    """
    API endpoint to get woredas for a given region and zone.
    Uses database-first approach with fallback.
    """
    try:
        region = request.GET.get('region')
        zone = request.GET.get('zone')
        
        if not region or not zone:
            return JsonResponse({'error': 'Missing region or zone parameter'}, status=400)
        
        # Get agencies with fallback strategy
        agencies, source = get_agencies_with_fallback()
        
        # Extract unique woredas for the given region and zone
        woredas = list(set(
            agency.get('woreda', '') for agency in agencies 
            if (agency.get('region', '').lower() == region.lower() and 
                agency.get('zone', '').lower() == zone.lower() and 
                agency.get('woreda'))
        ))
        woredas.sort()
        
        response_data = {
            'woredas': woredas,
            'source': source,
            'region': region,
            'zone': zone
        }
        
        logger.info(f"Returned {len(woredas)} woredas for region '{region}', zone '{zone}' from {source}")
        return JsonResponse(response_data, safe=False)
    
    except Exception as e:
        logger.error(f"Error getting woredas: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@telegram_auth_required
@require_GET
def get_kebeles(request):
    """
    API endpoint to get kebeles for a given region, zone, and woreda.
    Uses database-first approach with fallback.
    """
    try:
        region = request.GET.get('region')
        zone = request.GET.get('zone')
        woreda = request.GET.get('woreda')
        
        if not region or not zone or not woreda:
            return JsonResponse({'error': 'Missing region, zone, or woreda parameter'}, status=400)
        
        # Get agencies with fallback strategy
        agencies, source = get_agencies_with_fallback()
        
        # Extract unique kebeles for the given region, zone, and woreda
        kebeles = list(set(
            agency.get('kebele', '') for agency in agencies 
            if (agency.get('region', '').lower() == region.lower() and 
                agency.get('zone', '').lower() == zone.lower() and 
                agency.get('woreda', '') == woreda and 
                agency.get('kebele'))
        ))
        kebeles.sort()
        
        response_data = {
            'kebeles': kebeles,
            'source': source,
            'region': region,
            'zone': zone,
            'woreda': woreda
        }
        
        logger.info(f"Returned {len(kebeles)} kebeles for region '{region}', zone '{zone}', woreda '{woreda}' from {source}")
        return JsonResponse(response_data, safe=False)
    
    except Exception as e:
        logger.error(f"Error getting kebeles: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@telegram_auth_required
@require_GET
def all_agencies(request):
    """
    API endpoint to get all agencies with metadata about the data source.
    """
    try:
        # Get agencies with fallback strategy
        agencies, source = get_agencies_with_fallback()
        
        response_data = {
            'agencies': agencies,
            'source': source,
            'count': len(agencies),
            'timestamp': cache.get('agencies_last_updated', 'unknown')
        }
        
        logger.info(f"Returned {len(agencies)} total agencies from {source}")
        return JsonResponse(response_data, safe=False)
    
    except Exception as e:
        logger.error(f"Error getting all agencies: {e}")
        return JsonResponse({'error': str(e)}, status=500) 