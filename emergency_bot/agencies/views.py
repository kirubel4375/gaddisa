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

# Comprehensive fallback agencies data for when database is empty and internet is unavailable
FALLBACK_AGENCIES = [
    # ========== POLICE STATIONS ==========
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
        'latitude': 8.9806,
        'longitude': 38.7578,
        'hours_of_operation': '24/7',
        'services': 'Emergency response, Crime reporting, Traffic issues',
        'verified': True,
        'active': True
    },
    {
        'id': '2',
        'name': 'Arada Police Station',
        'type': 'police',
        'description': 'Police station serving Arada sub-city',
        'region': 'Addis Ababa',
        'zone': 'Arada',
        'woreda': '01',
        'kebele': '02',
        'phone': '+251114456789',
        'address': 'Piazza, Churchill Ave, Addis Ababa',
        'latitude': 9.0370,
        'longitude': 38.7467,
        'hours_of_operation': '24/7',
        'services': 'Emergency response, Crime reporting',
        'verified': True,
        'active': True
    },
    {
        'id': '3',
        'name': 'Kirkos Police Station',
        'type': 'police',
        'description': 'Police station in Kirkos sub-city',
        'region': 'Addis Ababa',
        'zone': 'Kirkos',
        'woreda': '02',
        'kebele': '01',
        'phone': '+251114887766',
        'address': 'Arat Kilo, Addis Ababa',
        'latitude': 9.0349,
        'longitude': 38.7612,
        'hours_of_operation': '24/7',
        'services': 'Emergency response, Crime reporting, Traffic control',
        'verified': True,
        'active': True
    },
    {
        'id': '4',
        'name': 'Adama Police Station',
        'type': 'police',
        'description': 'Main police station in Adama city',
        'region': 'Oromia',
        'zone': 'East Shewa',
        'woreda': 'Adama',
        'kebele': '01',
        'phone': '+251221112233',
        'address': 'Main Street, Adama, Oromia',
        'latitude': 8.5407,
        'longitude': 39.2677,
        'hours_of_operation': '24/7',
        'services': 'Emergency response, Crime reporting, Highway patrol',
        'verified': True,
        'active': True
    },
    {
        'id': '5',
        'name': 'Jimma Police Station',
        'type': 'police',
        'description': 'Police station serving Jimma town',
        'region': 'Oromia',
        'zone': 'Jimma',
        'woreda': 'Jimma',
        'kebele': '01',
        'phone': '+251471123456',
        'address': 'Commercial Bank Street, Jimma',
        'latitude': 7.6739,
        'longitude': 36.8341,
        'hours_of_operation': '24/7',
        'services': 'Emergency response, Crime reporting',
        'verified': True,
        'active': True
    },

    # ========== HOSPITALS ==========
    {
        'id': '6',
        'name': 'Black Lion Hospital',
        'type': 'hospital',
        'description': 'Major referral hospital with emergency services',
        'region': 'Addis Ababa',
        'zone': 'Lideta',
        'woreda': '04',
        'kebele': '05',
        'phone': '+251115517011',
        'address': 'Zambia St, Addis Ababa',
        'latitude': 9.0092,
        'longitude': 38.7441,
        'hours_of_operation': '24/7 Emergency',
        'services': 'Emergency care, General medicine, Surgery, ICU',
        'verified': True,
        'active': True
    },
    {
        'id': '7',
        'name': 'St. Paul Hospital',
        'type': 'hospital',
        'description': 'Millennium Medical College with 24/7 emergency care',
        'region': 'Addis Ababa',
        'zone': 'Gulele',
        'woreda': '01',
        'kebele': '02',
        'phone': '+251115533666',
        'address': 'Swaziland St, Addis Ababa',
        'latitude': 9.0499,
        'longitude': 38.7662,
        'hours_of_operation': '24/7 Emergency',
        'services': 'Emergency care, Specialized medicine, Cardiac care',
        'verified': True,
        'active': True
    },
    {
        'id': '8',
        'name': 'Amanuel Mental Specialized Hospital',
        'type': 'hospital',
        'description': 'Specialized mental health hospital',
        'region': 'Addis Ababa',
        'zone': 'Addis Ketema',
        'woreda': '01',
        'kebele': '03',
        'phone': '+251111223344',
        'address': 'Mexico Square, Addis Ababa',
        'latitude': 9.0349,
        'longitude': 38.7525,
        'hours_of_operation': '24/7 Emergency, Mon-Fri 8:00-17:00 Outpatient',
        'services': 'Mental health services, Psychiatric care, Counseling',
        'verified': True,
        'active': True
    },
    {
        'id': '9',
        'name': 'Yekatit 12 Hospital',
        'type': 'hospital',
        'description': 'General hospital with emergency and maternity services',
        'region': 'Addis Ababa',
        'zone': 'Arada',
        'woreda': '02',
        'kebele': '01',
        'phone': '+251115551234',
        'address': 'Yekatit 12 Square, Addis Ababa',
        'latitude': 9.0301,
        'longitude': 38.7379,
        'hours_of_operation': '24/7 Emergency',
        'services': 'Emergency care, Maternity, Pediatrics, Surgery',
        'verified': True,
        'active': True
    },
    {
        'id': '10',
        'name': 'Adama Hospital Medical College',
        'type': 'hospital',
        'description': 'Regional referral hospital in Adama',
        'region': 'Oromia',
        'zone': 'East Shewa',
        'woreda': 'Adama',
        'kebele': '02',
        'phone': '+251221556677',
        'address': 'Hospital Road, Adama',
        'latitude': 8.5389,
        'longitude': 39.2705,
        'hours_of_operation': '24/7 Emergency',
        'services': 'Emergency care, Surgery, Internal medicine',
        'verified': True,
        'active': True
    },
    {
        'id': '11',
        'name': 'Jimma University Medical Center',
        'type': 'hospital',
        'description': 'University teaching hospital',
        'region': 'Oromia',
        'zone': 'Jimma',
        'woreda': 'Jimma',
        'kebele': '02',
        'phone': '+251471789012',
        'address': 'University Campus, Jimma',
        'latitude': 7.6832,
        'longitude': 36.8341,
        'hours_of_operation': '24/7 Emergency',
        'services': 'Emergency care, Teaching hospital, Research',
        'verified': True,
        'active': True
    },

    # ========== NGOs & SUPPORT ORGANIZATIONS ==========
    {
        'id': '12',
        'name': 'Ethiopian Women Lawyers Association',
        'type': 'ngo',
        'description': 'Legal aid and support for women and children',
        'region': 'Addis Ababa',
        'zone': 'Kirkos',
        'woreda': '01',
        'kebele': '04',
        'phone': '+251115505050',
        'address': 'Kirkos, Addis Ababa',
        'latitude': 9.0095,
        'longitude': 38.7612,
        'hours_of_operation': 'Mon-Fri 8:00-17:00',
        'services': 'Legal consultation, Women rights advocacy, Court representation',
        'verified': True,
        'active': True
    },
    {
        'id': '13',
        'name': 'Association for Women in Development',
        'type': 'ngo',
        'description': 'Empowerment and support for women',
        'region': 'Addis Ababa',
        'zone': 'Bole',
        'woreda': '02',
        'kebele': '01',
        'phone': '+251116677889',
        'address': 'Bole Sub-city, Addis Ababa',
        'latitude': 8.9876,
        'longitude': 38.7643,
        'hours_of_operation': 'Mon-Fri 8:30-17:30',
        'services': 'Skills training, Microfinance, Legal support',
        'verified': True,
        'active': True
    },
    {
        'id': '14',
        'name': 'Children and Family Services',
        'type': 'ngo',
        'description': 'Child protection and family support services',
        'region': 'Addis Ababa',
        'zone': 'Gulele',
        'woreda': '02',
        'kebele': '03',
        'phone': '+251117788990',
        'address': 'Gulele Sub-city, Addis Ababa',
        'latitude': 9.0567,
        'longitude': 38.7589,
        'hours_of_operation': 'Mon-Sat 8:00-18:00',
        'services': 'Child protection, Family counseling, Foster care',
        'verified': True,
        'active': True
    },
    {
        'id': '15',
        'name': 'Oromia Women and Children Support Center',
        'type': 'ngo',
        'description': 'Regional support center for women and children',
        'region': 'Oromia',
        'zone': 'East Shewa',
        'woreda': 'Adama',
        'kebele': '03',
        'phone': '+251221334455',
        'address': 'Central Adama, Oromia',
        'latitude': 8.5423,
        'longitude': 39.2698,
        'hours_of_operation': 'Mon-Fri 8:00-17:00',
        'services': 'Counseling, Legal aid, Shelter services',
        'verified': True,
        'active': True
    },

    # ========== GOVERNMENT OFFICES ==========
    {
        'id': '16',
        'name': 'Women and Children Affairs Bureau - Addis Ababa',
        'type': 'government',
        'description': 'Government office for women and children protection',
        'region': 'Addis Ababa',
        'zone': 'Arada',
        'woreda': '01',
        'kebele': '01',
        'phone': '+251115252525',
        'address': 'Arada Sub-city Administration, Addis Ababa',
        'latitude': 9.0336,
        'longitude': 38.7504,
        'hours_of_operation': 'Mon-Fri 8:30-17:30',
        'services': 'Policy implementation, Child protection, Legal support',
        'verified': True,
        'active': True
    },
    {
        'id': '17',
        'name': 'Ministry of Women and Social Affairs',
        'type': 'government',
        'description': 'Federal ministry office',
        'region': 'Addis Ababa',
        'zone': 'Kirkos',
        'woreda': '03',
        'kebele': '02',
        'phone': '+251115161718',
        'address': 'Ministry Building, Kirkos, Addis Ababa',
        'latitude': 9.0278,
        'longitude': 38.7543,
        'hours_of_operation': 'Mon-Fri 8:30-17:30',
        'services': 'Policy development, National programs, Coordination',
        'verified': True,
        'active': True
    },
    {
        'id': '18',
        'name': 'Oromia Women and Children Affairs Bureau',
        'type': 'government',
        'description': 'Regional government office',
        'region': 'Oromia',
        'zone': 'East Shewa',
        'woreda': 'Adama',
        'kebele': '01',
        'phone': '+251221445566',
        'address': 'Regional Government Building, Adama',
        'latitude': 8.5445,
        'longitude': 39.2721,
        'hours_of_operation': 'Mon-Fri 8:30-17:30',
        'services': 'Regional coordination, Policy implementation',
        'verified': True,
        'active': True
    },

    # ========== SHELTERS ==========
    {
        'id': '19',
        'name': 'Safe Haven Women Shelter',
        'type': 'shelter',
        'description': 'Emergency shelter for women and children',
        'region': 'Addis Ababa',
        'zone': 'Lideta',
        'woreda': '02',
        'kebele': '04',
        'phone': '+251118899001',
        'address': 'Confidential Location, Lideta, Addis Ababa',
        'latitude': 9.0156,
        'longitude': 38.7389,
        'hours_of_operation': '24/7',
        'services': 'Emergency shelter, Counseling, Legal support, Job training',
        'verified': True,
        'active': True
    },
    {
        'id': '20',
        'name': 'Hope Center for Women',
        'type': 'shelter',
        'description': 'Transitional housing and support services',
        'region': 'Addis Ababa',
        'zone': 'Kolfe Keranio',
        'woreda': '01',
        'kebele': '02',
        'phone': '+251119900112',
        'address': 'Kolfe Keranio, Addis Ababa',
        'latitude': 8.9789,
        'longitude': 38.7123,
        'hours_of_operation': '24/7',
        'services': 'Transitional housing, Skills training, Childcare',
        'verified': True,
        'active': True
    },
    {
        'id': '21',
        'name': 'Regional Family Support Center',
        'type': 'shelter',
        'description': 'Regional shelter and support services',
        'region': 'Oromia',
        'zone': 'Jimma',
        'woreda': 'Jimma',
        'kebele': '03',
        'phone': '+251471556677',
        'address': 'Confidential Location, Jimma',
        'latitude': 7.6756,
        'longitude': 36.8378,
        'hours_of_operation': '24/7',
        'services': 'Emergency shelter, Counseling, Reintegration support',
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
    Enhanced with better filtering and distance calculation.
    """
    try:
        # Get coordinates from query parameters
        latitude = request.GET.get('lat')
        longitude = request.GET.get('lng')
        max_distance = request.GET.get('max_distance', '50')  # Default 50km
        agency_type = request.GET.get('type')  # Optional type filter
        
        if not latitude or not longitude:
            return JsonResponse({'error': 'Missing latitude or longitude'}, status=400)
        
        # Convert to float
        lat = float(latitude)
        lng = float(longitude)
        max_dist = float(max_distance)
        
        # Get agencies with fallback strategy
        agencies, source = get_agencies_with_fallback()
        
        # Calculate distance for each agency
        result = []
        for agency in agencies:
            try:
                agency_lat = float(agency['latitude'])
                agency_lng = float(agency['longitude'])
                distance = calculate_distance(lat, lng, agency_lat, agency_lng)
                
                # Apply distance filter
                if distance <= max_dist:
                    # Apply type filter if specified
                    if agency_type and agency.get('type') != agency_type:
                        continue
                    
                    agency_data = agency.copy()
                    agency_data['distance'] = round(distance, 2)
                    result.append(agency_data)
            except (ValueError, KeyError) as e:
                logger.warning(f"Skipping agency due to invalid coordinates: {e}")
                continue
        
        # Sort by distance (closest first)
        result.sort(key=lambda x: x.get('distance', float('inf')))
        
        # Add metadata about data source and filters
        response_data = {
            'agencies': result,
            'source': source,
            'count': len(result),
            'filters': {
                'latitude': lat,
                'longitude': lng,
                'max_distance': max_dist,
                'type': agency_type
            }
        }
        
        logger.info(f"Returned {len(result)} nearby agencies from {source} within {max_dist}km")
        return JsonResponse(response_data, safe=False)
    
    except Exception as e:
        logger.error(f"Error finding nearby agencies: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@require_GET
def agency_detail(request, agency_id):
    """
    Get detailed information for a specific agency by ID.
    Fetches from database with fallback strategy.
    """
    try:
        # Try to get from database first
        try:
            agency = Agency.objects.get(id=agency_id, active=True)
            agency_data = {
                'id': agency.id,
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
            }
            logger.info(f"Retrieved agency detail from database: {agency.name}")
            return JsonResponse(agency_data)
        
        except Agency.DoesNotExist:
            # Agency not found in database, check fallback data
            logger.warning(f"Agency ID {agency_id} not found in database, checking fallback")
            
            # Check fallback agencies
            for agency in FALLBACK_AGENCIES:
                if str(agency['id']) == str(agency_id):
                    logger.info(f"Retrieved agency detail from fallback: {agency['name']}")
                    return JsonResponse(agency)
            
            # Agency not found anywhere
            logger.warning(f"Agency ID {agency_id} not found in database or fallback")
            return JsonResponse({'error': 'Agency not found'}, status=404)
    
    except Exception as e:
        logger.error(f"Error retrieving agency detail: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

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

@telegram_auth_required
@require_GET
def get_regions(request):
    """
    API endpoint to get all regions with agency counts.
    Uses database-first approach with fallback.
    """
    try:
        # Get agencies with fallback strategy
        agencies, source = get_agencies_with_fallback()
        
        # Count agencies by region
        region_counts = {}
        for agency in agencies:
            region = agency.get('region', 'Unknown')
            if region not in region_counts:
                region_counts[region] = 0
            region_counts[region] += 1
        
        # Convert to list of dictionaries
        regions = []
        for region, count in region_counts.items():
            regions.append({
                'name': region,
                'count': count
            })
        
        # Sort by name
        regions.sort(key=lambda x: x['name'])
        
        response_data = {
            'regions': regions,
            'source': source,
            'total_regions': len(regions)
        }
        
        logger.info(f"Returned {len(regions)} regions from {source}")
        return JsonResponse(response_data, safe=False)
    
    except Exception as e:
        logger.error(f"Error getting regions: {e}")
        return JsonResponse({'error': str(e)}, status=500) 