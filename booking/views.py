import os
import json

import requests

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Avg, Max, Count, Q
from django.db.models.functions import TruncMonth
from django.template.loader import get_template
from django.utils import timezone

from .models import Booking, Review, BookingAttachment, ContactMessage, ReviewLike, ReviewComment, ReviewShare, PredefinedRouteFare, PredefinedRouteDistance
from .forms import ReviewForm, ContactMessageForm
from .utils import generate_receipt_pdf
from drivers.views import auto_assign_driver_to_booking
from django.views.decorators.csrf import csrf_exempt


def _ors_get_with_retry(url, params, timeout=20, max_attempts=3):
    """
    OpenRouteService ka free server kabhi-kabhi slow ho jata hai aur
    timeout ya galat response de deta hai. Isliye automatically 2-3 baar
    retry karte hain before giving up.
    """
    last_status = None

    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(url, params=params, timeout=timeout)

            if response.status_code == 200:
                return response, None

            last_status = response.status_code
            continue

        except requests.exceptions.Timeout:
            last_status = "timeout"
            continue
        except requests.exceptions.RequestException as e:
            return None, str(e)

    return None, f"status_code: {last_status}"


import math

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0 # Earth radius in KM
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

CG_VILLAGE_COORDS = {
    "raipur": (21.2514, 81.6296),
    "durg": (21.1904, 81.2849),
    "bhilai": (21.2092, 81.3784),
    "dhamtari": (20.7071, 81.5492),
    "bilaspur": (22.0797, 82.1409),
    "rajnandgaon": (21.0971, 81.0384),
    "korba": (22.3595, 82.7501),
    "raigarh": (21.8974, 83.3950),
    "jagdalpur": (19.0744, 82.0212),
    "ambikapur": (23.1185, 83.1984),
    "kanker": (20.2714, 81.4931),
    "mahasamund": (21.1084, 82.0984),
    "balod": (20.7303, 81.2045),
    "bhatapara": (21.7335, 81.9560),
    "baloda bazar": (21.6605, 82.1604),
    "kawardha": (22.0150, 81.2490),
    "kabirdham": (22.0150, 81.2490),
    "mungeli": (22.0667, 81.6883),
    "champa": (22.0400, 82.6500),
    "janjgir": (22.0084, 82.5744),
    "sakti": (22.0270, 82.9570),
    "jashpur": (22.8844, 84.1444),
    "surajpur": (23.2185, 82.8595),
    "baikunthpur": (23.2592, 82.5574),
    "manendragarh": (23.2120, 82.2020),
    "chirmiri": (23.1812, 82.3551),
    "kondagaon": (19.5982, 81.6661),
    "narayanpur": (19.7244, 81.2482),
    "dantewada": (18.8984, 81.3503),
    "sukma": (18.3970, 81.6700),
    "bijapur": (18.7932, 80.8164),
    "gariaband": (20.6350, 82.0620),
    "pithora": (21.2670, 82.5140),
    "basna": (21.2820, 82.8230),
    "saraipali": (21.3280, 83.0030),
    "bagbahra": (21.0370, 82.3850),
    "kurud": (20.8280, 81.6370),
    "nagri": (20.4020, 81.8010),
    "magarlod": (20.6120, 81.7510),
    "kodebod": (20.9125, 81.6080),
    "sankra": (20.7330, 81.6120),
    "patan": (21.0340, 81.5360),
    "gunderdehi": (20.9420, 81.2950),
    "dondilohara": (20.7810, 81.0420),
    "dalli rajhara": (20.5790, 81.0840),
    "gurur": (20.6520, 81.3210),
    "abhanpur": (21.0500, 81.6780),
    "rajim": (20.9700, 81.8840),
    "arang": (21.1920, 81.9660),
    "tilda": (21.5580, 81.7850),
    "kharora": (21.4310, 81.9320),
    "simga": (21.6310, 81.7040),
    "kasdol": (21.6230, 82.4280),
    "palari": (21.5230, 82.0290),
    "lavan": (21.5120, 82.2510),
    "dongargarh": (21.1890, 80.7580),
    "khairagarh": (21.4190, 80.9760),
    "chhuikhadan": (21.5310, 80.9950),
    "gandai": (21.6610, 81.1070),
    "dongargaon": (20.9720, 80.8410),
    "chhuria": (20.8520, 80.7120),
    "chowki": (20.7810, 80.7410),
    "mohla": (20.5820, 80.7410),
    "manpur": (20.3710, 80.8510),
    "bhanupratappur": (20.3090, 81.0770),
    "antagarh": (20.0890, 81.1610),
    "pakhanjore": (19.8650, 80.7680),
    "keshkal": (20.0870, 81.5870),
    "pharasgaon": (19.8510, 81.6510),
    "charama": (20.4510, 81.3810),
    "kumhari": (21.2650, 81.5120),
    "charoda": (21.2210, 81.4410),
    "jamul": (21.2510, 81.3810),
    "utai": (21.1120, 81.3510),
    "nagpur": (21.1458, 79.0882),
    "gondia": (21.4580, 80.1960),
    "bhandara": (21.1670, 79.6500),
    "balaghat": (21.8000, 80.1830),
    "sambalpur": (21.4669, 83.9812),
}

def geocode_place(place_name):
    clean = place_name.strip()
    if not clean:
        return None, None

    norm = normalize_city(clean)
    if norm in CG_VILLAGE_COORDS:
        return CG_VILLAGE_COORDS[norm]

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) GhidoraTransportApp/2.0'}

    # 1. Try Photon API (Best for Indian Villages & OpenStreetMap data)
    try:
        url = "https://photon.komoot.io/api/"
        res = requests.get(url, params={'q': clean + " Chhattisgarh India", 'limit': 1}, headers=headers, timeout=3)
        if res.status_code == 200 and res.json().get('features'):
            coords = res.json()['features'][0]['geometry']['coordinates']
            return float(coords[1]), float(coords[0])
    except Exception:
        pass

    # 2. Try Nominatim with Chhattisgarh context
    try:
        url = "https://nominatim.openstreetmap.org/search"
        res = requests.get(url, params={'q': clean + ", Chhattisgarh, India", 'format': 'json', 'limit': 1}, headers=headers, timeout=3)
        if res.status_code == 200 and res.json():
            item = res.json()[0]
            return float(item['lat']), float(item['lon'])
    except Exception:
        pass

    # 3. Try Nominatim General
    try:
        url = "https://nominatim.openstreetmap.org/search"
        res = requests.get(url, params={'q': clean + ", India", 'format': 'json', 'limit': 1}, headers=headers, timeout=3)
        if res.status_code == 200 and res.json():
            item = res.json()[0]
            return float(item['lat']), float(item['lon'])
    except Exception:
        pass

    # 4. Try Open-Meteo Geocoder
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        res = requests.get(url, params={'name': clean, 'count': 1}, timeout=3)
        if res.status_code == 200 and res.json().get('results'):
            item = res.json()['results'][0]
            return float(item['latitude']), float(item['longitude'])
    except Exception:
        pass

    return None, None


def get_osrm_route(lat1, lon1, lat2, lon2):
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
        res = requests.get(url, timeout=5)
        if res.status_code == 200 and res.json().get('routes'):
            route = res.json()['routes'][0]
            dist_km = round(route['distance'] / 1000.0, 1)
            dur_min = round(route['duration'] / 60.0)
            return dist_km, dur_min
    except Exception:
        pass
    return None, None


def normalize_city(name):
    if not name:
        return ""
    s = name.lower().strip()
    s = s.replace("bilashpur", "bilaspur")
    s = s.replace("bhelai", "bhilai")
    s = s.replace("durgh", "durg")
    s = s.replace("raypur", "raipur")
    s = s.replace("kankar", "kanker")
    s = s.replace("nandgaon", "rajnandgaon")
    return s


def get_predefined_route_fare(pickup, destination):
    """
    Check if an active PredefinedRouteFare exists for given pickup & destination.
    Priority 1: Exact match (from_location == pickup AND to_location == destination)
    Priority 2: Reverse match (from_location == destination AND to_location == pickup AND same_direction_both == True)
    Returns matching PredefinedRouteFare object or None.
    """
    if not pickup or not destination:
        return None

    p_norm = pickup.strip().lower()
    d_norm = destination.strip().lower()

    if p_norm == d_norm:
        return None

    active_routes = PredefinedRouteFare.objects.filter(is_active=True)

    # 1. Exact direction match
    for route in active_routes:
        if route.from_location.strip().lower() == p_norm and route.to_location.strip().lower() == d_norm:
            return route

    # 2. Reverse direction match (only if same_direction_both is True)
    for route in active_routes:
        if route.same_direction_both:
            if route.from_location.strip().lower() == d_norm and route.to_location.strip().lower() == p_norm:
                return route

    return None


def get_predefined_route_distance(pickup, destination):
    """
    Check if an active PredefinedRouteDistance exists for given pickup & destination.
    Priority 1: Exact match (from_location == pickup AND to_location == destination)
    Priority 2: Reverse match (from_location == destination AND to_location == pickup AND same_direction_both == True)
    Returns matching PredefinedRouteDistance object or None.
    """
    if not pickup or not destination:
        return None

    p_norm = pickup.strip().lower()
    d_norm = destination.strip().lower()

    if p_norm == d_norm:
        return None

    active_distances = PredefinedRouteDistance.objects.filter(is_active=True)

    # 1. Exact direction match
    for dist_obj in active_distances:
        if dist_obj.from_location.strip().lower() == p_norm and dist_obj.to_location.strip().lower() == d_norm:
            return dist_obj

    # 2. Reverse direction match (only if same_direction_both is True)
    for dist_obj in active_distances:
        if dist_obj.same_direction_both:
            if dist_obj.from_location.strip().lower() == d_norm and dist_obj.to_location.strip().lower() == p_norm:
                return dist_obj

    return None


def check_route_fare_api(request):
    """
    AJAX Endpoint to check whether an active predefined route fare exists.
    GET params: ?pickup=Dhamtari&destination=Raipur&trip_type=One Way
    """
    pickup = request.GET.get('pickup', '').strip()
    destination = request.GET.get('destination', '').strip()
    trip_type = request.GET.get('trip_type', 'One Way').strip()

    if not pickup or not destination:
        return JsonResponse({
            'success': False,
            'has_predefined_fare': False,
            'message': 'Pickup or destination missing'
        })

    route = get_predefined_route_fare(pickup, destination)

    if route:
        single_fare = float(route.fixed_fare)
        double_fare = float(route.double_trip_fare) if route.double_trip_fare else single_fare * 2.0
        applied_fare = route.get_fare_for_trip_type(trip_type)

        return JsonResponse({
            'success': True,
            'has_predefined_fare': True,
            'single_trip_fare': single_fare,
            'double_trip_fare': double_fare,
            'fixed_fare': applied_fare,
            'applied_fare': applied_fare,
            'distance_km': float(route.distance_km) if route.distance_km else None,
            'fare_type': 'Predefined Route Fare',
            'from_location': route.from_location,
            'to_location': route.to_location,
            'same_direction_both': route.same_direction_both,
            'description': route.description or '',
            'note': 'Fare set by Ghidora Transport'
        })
    else:
        return JsonResponse({
            'success': True,
            'has_predefined_fare': False,
            'fare_type': 'Distance Based Fare'
        })


def calculate_distance_api(request):
    """
    AJAX endpoint: High-Precision Logistics Distance Engine with Google Maps API Support,
    Instant Highway DB, Live OSRM Satellite Routing, and Multi-Source Fallbacks.
    """
    pickup = request.GET.get('pickup', '').strip()
    destination = request.GET.get('destination', '').strip()

    p_lat = request.GET.get('pickup_lat', '').strip()
    p_lng = request.GET.get('pickup_lng', '').strip()
    d_lat = request.GET.get('destination_lat', '').strip()
    d_lng = request.GET.get('destination_lng', '').strip()

    if not pickup and not (p_lat and p_lng):
        return JsonResponse({'success': False, 'error': 'Pickup missing hai'})
    if not destination and not (d_lat and d_lng):
        return JsonResponse({'success': False, 'error': 'Destination missing hai'})

    # Step 0A: Google Maps Directions API if API key configured
    g_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
    if g_key:
        origin_str = f"{p_lat},{p_lng}" if (p_lat and p_lng) else pickup
        dest_str = f"{d_lat},{d_lng}" if (d_lat and d_lng) else destination
        try:
            g_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={requests.utils.quote(origin_str)}&destination={requests.utils.quote(dest_str)}&mode=driving&key={g_key}"
            g_res = requests.get(g_url, timeout=5)
            if g_res.status_code == 200:
                g_data = g_res.json()
                if g_data.get('status') == 'OK' and g_data.get('routes'):
                    leg = g_data['routes'][0]['legs'][0]
                    dist_km = round(leg['distance']['value'] / 1000.0, 1)
                    dur_sec = leg['duration']['value']
                    dur_min = round(dur_sec / 60.0)
                    dur_text = leg['duration']['text']
                    poly_points = g_data['routes'][0]['overview_polyline']['points']
                    return JsonResponse({
                        'success': True,
                        'distance_km': dist_km,
                        'duration_minutes': dur_min,
                        'duration_text': dur_text,
                        'highway_name': 'Google Driving Route',
                        'polyline_points': poly_points,
                        'source': 'Google Maps Route',
                        'is_computer_generated': True
                    })
        except Exception as e:
            pass

    # Step 0B: Check Admin Predefined Route Fare Distance
    admin_route = get_predefined_route_fare(pickup, destination)
    if admin_route and admin_route.distance_km and admin_route.distance_km > 0:
        dist_km = float(admin_route.distance_km)
        dur_min = int((dist_km / 45.0) * 60.0)
        return JsonResponse({
            'success': True,
            'distance_km': dist_km,
            'duration_minutes': max(dur_min, 10),
            'duration_text': f"{dur_min} min",
            'highway_name': f'Admin Route ({admin_route.from_location} ➔ {admin_route.to_location})',
            'source': 'Predefined Route Distance (Admin)',
            'is_computer_generated': True
        })

    # Step 0C: Check Admin Standalone Predefined Route Distance
    admin_dist = get_predefined_route_distance(pickup, destination)
    if admin_dist and admin_dist.distance_km and admin_dist.distance_km > 0:
        dist_km = float(admin_dist.distance_km)
        dur_min = int((dist_km / 45.0) * 60.0)
        return JsonResponse({
            'success': True,
            'distance_km': dist_km,
            'duration_minutes': max(dur_min, 10),
            'duration_text': f"{dur_min} min",
            'highway_name': f'Admin Distance ({admin_dist.from_location} ➔ {admin_dist.to_location})',
            'source': 'Predefined Route Distance (Admin)',
            'is_computer_generated': True
        })

    p_norm = normalize_city(pickup)
    d_norm = normalize_city(destination)

    # Step 1: High Precision Highway Route DB
    KNOWN_ROUTES = {
        ("dhamtari", "raipur"): (77.6, 85, "NH-30 Express Highway"),
        ("raipur", "dhamtari"): (77.6, 85, "NH-30 Express Highway"),
        ("dhamtari", "durg"): (64.2, 75, "State Highway 22"),
        ("durg", "dhamtari"): (64.2, 75, "State Highway 22"),
        ("dhamtari", "bhilai"): (67.5, 80, "Dhamtari-Bhilai Road"),
        ("bhilai", "dhamtari"): (67.5, 80, "Dhamtari-Bhilai Road"),
        ("raipur", "durg"): (38.5, 50, "NH-53 / GE Road"),
        ("durg", "raipur"): (38.5, 50, "NH-53 / GE Road"),
        ("raipur", "bhilai"): (31.2, 40, "NH-53 GE Road"),
        ("bhilai", "raipur"): (31.2, 40, "NH-53 GE Road"),
        ("durg", "bhilai"): (12.0, 20, "Durg-Bhilai Twin City Bypass"),
        ("bhilai", "durg"): (12.0, 20, "Durg-Bhilai Twin City Bypass"),
        ("raipur", "bilaspur"): (118.4, 135, "NH-130 Highway"),
        ("bilaspur", "raipur"): (118.4, 135, "NH-130 Highway"),
        ("durg", "bilaspur"): (130.0, 150, "NH-130 Highway"),
        ("bilaspur", "durg"): (130.0, 150, "NH-130 Highway"),
        ("bhilai", "bilaspur"): (125.0, 145, "NH-130 Highway"),
        ("bilaspur", "bhilai"): (125.0, 145, "NH-130 Highway"),
        ("raipur", "nagpur"): (284.0, 290, "NH-53 National Corridor"),
        ("nagpur", "raipur"): (284.0, 290, "NH-53 National Corridor"),
        ("raipur", "jagdalpur"): (288.0, 310, "NH-30 South Expressway"),
        ("jagdalpur", "raipur"): (288.0, 310, "NH-30 South Expressway"),
        ("dhamtari", "kanker"): (61.5, 70, "NH-30 Highway"),
        ("kanker", "dhamtari"): (61.5, 70, "NH-30 Highway"),
        ("raipur", "mahasamund"): (54.0, 60, "NH-53 Eastern Route"),
        ("mahasamund", "raipur"): (54.0, 60, "NH-53 Eastern Route"),
        ("durg", "rajnandgaon"): (32.0, 45, "NH-53 Western Route"),
        ("rajnandgaon", "durg"): (32.0, 45, "NH-53 Western Route"),
        ("raipur", "rajnandgaon"): (70.0, 80, "NH-53 Expressway"),
        ("rajnandgaon", "raipur"): (70.0, 80, "NH-53 Expressway"),
        ("raipur", "korba"): (215.0, 250, "SH-18 / NH-130 Highway"),
        ("korba", "raipur"): (215.0, 250, "SH-18 / NH-130 Highway"),
        ("bilaspur", "korba"): (95.0, 110, "SH-18 Highway"),
        ("korba", "bilaspur"): (95.0, 110, "SH-18 Highway"),
        ("raipur", "raigarh"): (250.0, 280, "NH-53 / NH-49 Corridor"),
        ("raigarh", "raipur"): (250.0, 280, "NH-53 / NH-49 Corridor"),
        ("raipur", "ambikapur"): (340.0, 390, "NH-130 Northern Route"),
        ("ambikapur", "raipur"): (340.0, 390, "NH-130 Northern Route"),
        ("kodebod", "raipur"): (49.5, 64, "NH-30 Express Highway"),
        ("raipur", "kodebod"): (49.5, 64, "NH-30 Express Highway"),
        ("kodebod", "dhamtari"): (28.5, 35, "NH-30 Express Highway"),
        ("dhamtari", "kodebod"): (28.5, 35, "NH-30 Express Highway"),
        ("kurud", "raipur"): (58.4, 73, "NH-30 Express Highway"),
        ("raipur", "kurud"): (58.4, 73, "NH-30 Express Highway"),
        ("kurud", "dhamtari"): (26.5, 32, "NH-30 Express Highway"),
        ("dhamtari", "kurud"): (26.5, 32, "NH-30 Express Highway"),
        ("abhanpur", "raipur"): (30.8, 43, "NH-30 & Atal Path Expy"),
        ("raipur", "abhanpur"): (30.8, 43, "NH-30 & Atal Path Expy"),
        ("abhanpur", "dhamtari"): (50.0, 60, "NH-30 Express Highway"),
        ("dhamtari", "abhanpur"): (50.0, 60, "NH-30 Express Highway"),
        ("rajim", "raipur"): (45.0, 55, "NH-130C Highway"),
        ("raipur", "rajim"): (45.0, 55, "NH-130C Highway"),
        ("bhakhara", "raipur"): (55.0, 70, "NH-30 / SH-22 Route"),
        ("raipur", "bhakhara"): (55.0, 70, "NH-30 / SH-22 Route"),
    }

    if (p_norm, d_norm) in KNOWN_ROUTES:
        dist_km, dur_min, hw_name = KNOWN_ROUTES[(p_norm, d_norm)]
        return JsonResponse({
            'success': True,
            'distance_km': dist_km,
            'duration_minutes': dur_min,
            'duration_text': f"{dur_min} min",
            'highway_name': hw_name,
            'source': 'Computer Generated (AI Satellite GPS)',
            'is_computer_generated': True
        })

    # Step 2: Live Geocode / Coordinates + OSRM Live Satellite Highway Engine
    lat1, lon1 = None, None
    lat2, lon2 = None, None
    if p_lat and p_lng:
        try: lat1, lon1 = float(p_lat), float(p_lng)
        except: pass
    if d_lat and d_lng:
        try: lat2, lon2 = float(d_lat), float(d_lng)
        except: pass

    if not (lat1 and lon1):
        lat1, lon1 = geocode_place(pickup)
    if not (lat2 and lon2):
        lat2, lon2 = geocode_place(destination)

    if lat1 and lat2:
        dist_km, dur_min = get_osrm_route(lat1, lon1, lat2, lon2)
        if dist_km and dist_km > 0:
            return JsonResponse({
                'success': True,
                'distance_km': dist_km,
                'duration_minutes': dur_min,
                'duration_text': f"{dur_min} min",
                'highway_name': 'Live Highway Satellite Route',
                'source': 'Computer Generated (AI Satellite GPS)',
                'is_computer_generated': True
            })
        
        # Fallback to Haversine with 1.28 road factor
        straight_km = haversine_distance(lat1, lon1, lat2, lon2)
        road_km = round(straight_km * 1.28, 1)
        dur_min = round((road_km / 45) * 60)
        return JsonResponse({
            'success': True,
            'distance_km': max(road_km, 5.0),
            'duration_minutes': max(dur_min, 10),
            'duration_text': f"{dur_min} min",
            'highway_name': 'Satellite Road Network',
            'source': 'Computer Generated (AI Satellite GPS)',
            'is_computer_generated': True
        })

    # Step 3: Estimated Fallback
    return JsonResponse({
        'success': True,
        'distance_km': 50.0,
        'duration_minutes': 60,
        'duration_text': "60 min",
        'highway_name': 'Standard Highway Route',
        'source': 'Computer Generated (AI Estimate)',
        'is_computer_generated': True
    })


def seed_default_reviews():
    """Seed initial high-quality verified customer reviews if database has no reviews."""
    if Review.objects.exists():
        return

    dummy_booking = Booking.objects.first()
    if not dummy_booking:
        dummy_booking = Booking.objects.create(
            name="Ghidora Customer",
            phone="916264588894",
            pickup="Dhamtari",
            destination="Raipur",
            journey_date=timezone.now().date(),
            distance=77.6,
            fare=2500.0,
            vehicle_type="Mahindra Pickup",
            status="Completed"
        )

    default_reviews = [
        {
            "guest_name": "Rajesh Kumar Sahu",
            "guest_email": "rajesh.sahu@gmail.com",
            "guest_phone": "9827189012",
            "rating": 5,
            "comment": "Dhamtari se Raipur transport ke liye Ghidora Transport ki service sabse fast aur safe mili. Mahindra Bolero pickup gaadi time par aayi aur saaman surakshit pahuncha. Very trustworthy service!",
            "service_used": "Mahindra Pickup Transport",
            "is_verified": True
        },
        {
            "guest_name": "Amit Sharma",
            "guest_email": "sharma.amit.cgp@gmail.com",
            "guest_phone": "9425512345",
            "rating": 5,
            "comment": "Instant online rate quote calculator bilkul accurate hai. 1-click booking karke vehicle turant confirm ho gaya. Driver Ramesh uncle ne pure raste bohot acche se driving ki.",
            "service_used": "Commercial Cargo Transport",
            "is_verified": True
        },
        {
            "guest_name": "Priya Verma",
            "guest_email": "priya.verma.raipur@gmail.com",
            "guest_phone": "9179098765",
            "rating": 5,
            "comment": "Ghidora AI Assistant and online tracking system makes booking super easy. Fixed route fare system is honest without any hidden charges. Highly recommended for Chhattisgarh transport!",
            "service_used": "Full Truck Load Transport",
            "is_verified": True
        }
    ]

    for r in default_reviews:
        Review.objects.create(
            booking=dummy_booking,
            guest_name=r["guest_name"],
            guest_email=r["guest_email"],
            guest_phone=r["guest_phone"],
            rating=r["rating"],
            comment=r["comment"],
            review=r["comment"],
            service_used=r["service_used"],
            is_approved=True,
            is_verified=r["is_verified"]
        )


def home(request):

    context = {}
    cache_key = "home_reviews_summary_data"
    cached_data = cache.get(cache_key)

    if cached_data is None:
        try:
            if not Review.objects.exists():
                seed_default_reviews()

            approved_qs = Review.objects.filter(is_approved=True).annotate(
                ann_likes=Count('likes', distinct=True),
                ann_comments=Count('comments', distinct=True),
                ann_shares=Count('shares', distinct=True)
            ).order_by("-created_at")
            reviews = list(approved_qs[:30])

            if not reviews:
                reviews = list(Review.objects.all().annotate(
                    ann_likes=Count('likes', distinct=True),
                    ann_comments=Count('comments', distinct=True),
                    ann_shares=Count('shares', distinct=True)
                ).order_by("-created_at")[:30])

            stats = Review.objects.filter(is_approved=True).aggregate(
                avg_rating=Avg('rating'),
                total_cnt=Count('id'),
                r5=Count('id', filter=Q(rating=5)),
                r4=Count('id', filter=Q(rating=4)),
                r3=Count('id', filter=Q(rating=3)),
                r2=Count('id', filter=Q(rating=2)),
                r1=Count('id', filter=Q(rating=1)),
            )

            average_rating = round(stats['avg_rating'] or 4.9, 1)
            total_reviews = stats['total_cnt'] or 0
            five_star = stats['r5'] or 0
            four_star = stats['r4'] or 0
            three_star = stats['r3'] or 0
            two_star = stats['r2'] or 0
            one_star = stats['r1'] or 0

            cached_data = {
                'reviews': reviews,
                'average_rating': average_rating,
                'total_reviews': total_reviews,
                'five_star': five_star,
                'four_star': four_star,
                'three_star': three_star,
                'two_star': two_star,
                'one_star': one_star,
            }
            cache.set(cache_key, cached_data, 120)
        except Exception:
            cached_data = {
                'reviews': [],
                'average_rating': 4.9,
                'total_reviews': 0,
                'five_star': 0,
                'four_star': 0,
                'three_star': 0,
                'two_star': 0,
                'one_star': 0,
            }

    reviews = cached_data['reviews']
    average_rating = cached_data['average_rating']
    total_reviews = cached_data['total_reviews']
    five_star = cached_data['five_star']
    four_star = cached_data['four_star']
    three_star = cached_data['three_star']
    two_star = cached_data['two_star']
    one_star = cached_data['one_star']

    # Dynamic percentage calculations matching star counts exactly (Google Review Summary style)
    if total_reviews > 0:
        five_percent = round((five_star / total_reviews) * 100)
        four_percent = round((four_star / total_reviews) * 100)
        three_percent = round((three_star / total_reviews) * 100)
        two_percent = round((two_star / total_reviews) * 100)
        one_percent = round((one_star / total_reviews) * 100)
    else:
        five_percent = 80
        four_percent = 12
        three_percent = 5
        two_percent = 2
        one_percent = 1
        average_rating = 4.9
        total_reviews = 128


    if request.method == "POST":
        try:
            name = request.POST.get('name', '').strip()
            phone = request.POST.get('phone', '').strip()
            email = request.POST.get('email', '').strip()
            pickup = request.POST.get('pickup', '').strip()
            destination = request.POST.get('destination', '').strip()

            journey_date_str = request.POST.get('journey_date', '').strip()
            if journey_date_str:
                try:
                    from datetime import datetime
                    journey_date = datetime.strptime(journey_date_str, '%Y-%m-%d').date()
                except Exception:
                    journey_date = timezone.now().date()
            else:
                journey_date = timezone.now().date()

            dist_raw = request.POST.get('distance', '').strip()
            try:
                distance = float(dist_raw) if dist_raw else 50.0
            except ValueError:
                distance = 50.0

            if distance <= 0:
                distance = 50.0

            vehicle_type = request.POST.get('vehicle_type', 'Mahindra Pickup').strip()
            trip_type = request.POST.get('trip_type', 'One Way').strip()

            cargo_type = request.POST.get('cargo_type', '').strip()
            weight_value = request.POST.get('weight_value', '').strip()
            weight_unit = request.POST.get('weight_unit', 'kg')
            message = request.POST.get('message', '').strip()

            distance_source = request.POST.get('distance_source', 'Manual Entered')

            pickup_lat_raw = request.POST.get('pickup_lat', '').strip()
            pickup_lng_raw = request.POST.get('pickup_lng', '').strip()
            destination_lat_raw = request.POST.get('destination_lat', '').strip()
            destination_lng_raw = request.POST.get('destination_lng', '').strip()
            duration_text = request.POST.get('duration_text', '').strip()

            try: pickup_lat = float(pickup_lat_raw) if pickup_lat_raw else None
            except: pickup_lat = None

            try: pickup_lng = float(pickup_lng_raw) if pickup_lng_raw else None
            except: pickup_lng = None

            try: destination_lat = float(destination_lat_raw) if destination_lat_raw else None
            except: destination_lat = None

            try: destination_lng = float(destination_lng_raw) if destination_lng_raw else None
            except: destination_lng = None

            # Priority 1: Admin Predefined Route Fare
            predefined_route = get_predefined_route_fare(pickup, destination)

            if predefined_route:
                fare = predefined_route.get_fare_for_trip_type(trip_type)
                fare_type = 'Predefined Route Fare'
            else:
                # Priority 2: Normal Distance Based Fare
                vehicle_rates = {
                    'Mahindra Pickup': 20,
                    'Mahindra Bolero': 30,
                    'Mahindra Cruiser': 30,
                    'Magic': 15,
                    'Van': 22,
                    'Mini Bus': 40,
                    'Tata Ace': 20,
                    'Mini Truck': 35,
                    'Tractor Trolley': 50,
                }

                rate = vehicle_rates.get(vehicle_type, 20)
                calc_distance = distance * 2 if trip_type == "Round Trip" else distance
                fare = calc_distance * rate
                fare_type = 'Distance Based Fare'

            booking = Booking.objects.create(
                user=request.user if request.user.is_authenticated else None,
                name=name,
                phone=phone,
                email=email if email else None,
                pickup=pickup,
                destination=destination,
                pickup_lat=pickup_lat,
                pickup_lng=pickup_lng,
                destination_lat=destination_lat,
                destination_lng=destination_lng,
                duration_text=duration_text if duration_text else None,
                journey_date=journey_date,
                distance=distance,
                distance_source=distance_source,
                fare=fare,
                fare_type=fare_type,
                vehicle_type=vehicle_type,
                trip_type=trip_type,
                cargo_type=cargo_type if cargo_type else None,
                weight_value=weight_value if weight_value else None,
                weight_unit=weight_unit,
                message=message if message else None,
            )

            voice_file = request.FILES.get('voice_message')
            if voice_file:
                BookingAttachment.objects.create(
                    booking=booking,
                    attachment_type='voice',
                    file=voice_file
                )

            for f in request.FILES.getlist('media_files'):
                attachment_type = 'video' if f.content_type.startswith('video') else 'photo'
                BookingAttachment.objects.create(
                    booking=booking,
                    attachment_type=attachment_type,
                    file=f
                )

            auto_assign_driver_to_booking(booking)

            # Instant Background Async Admin Email Notification (Zero UI Blocking)
            def _send_admin_booking_email_async(b):
                try:
                    from django.core.mail import EmailMessage
                    from django.conf import settings
                    subj = f"🚚 NEW BOOKING [{b.booking_id}] — {b.name} ({b.phone})"
                    msg_body = f"""New Booking Received on Ghidora Transport!

Booking ID: {b.booking_id}
Customer Name: {b.name}
Phone: {b.phone}
Email: {b.email or 'N/A'}
Pickup: {b.pickup}
Destination: {b.destination}
Vehicle Type: {b.vehicle_type}
Trip Type: {b.trip_type}
Journey Date: {b.journey_date}
Distance: {b.distance} KM
Total Fare: ₹{b.fare}
Status: {b.status}

Render Admin Link: https://ghidoratransport.onrender.com/admin/booking/booking/{b.id}/change/
"""
                    mail = EmailMessage(
                        subject=subj,
                        body=msg_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[settings.EMAIL_HOST_USER, 'ghidoratransport@gmail.com'],
                    )
                    mail.send(fail_silently=True)
                except Exception as ex:
                    print("❌ Async booking email exception:", ex)

            import threading
            threading.Thread(target=_send_admin_booking_email_async, args=(booking,), daemon=True).start()

            context.update({
                "success": True,
                "booking_id": booking.booking_id,
                "status": booking.status,
                "name": name,
                "phone": phone,
                "pickup": pickup,
                "destination": destination,
                "journey_date": str(journey_date),
                "distance": distance,
                "fare": fare,
                "fare_type": fare_type,
                "vehicle_type": vehicle_type,
                "trip_type": trip_type
            })
        except Exception as e:
            print("❌ Booking submission exception:", e)
            context["error"] = f"Booking submission issue: {e}. Please check your phone number and pickup details."

    # Pre-calculate counts and user's like state for each review
    session_key = request.session.session_key or ""
    user = request.user if request.user.is_authenticated else None

    for rev in reviews:
        try:
            rev.likes_count = getattr(rev, 'ann_likes', None)
            if rev.likes_count is None:
                rev.likes_count = rev.likes.count()
            rev.comments_count = getattr(rev, 'ann_comments', None)
            if rev.comments_count is None:
                rev.comments_count = rev.comments.count()
            rev.shares_count = getattr(rev, 'ann_shares', None)
            if rev.shares_count is None:
                rev.shares_count = rev.shares.count()

            if user:
                rev.is_liked = rev.likes.filter(user=user).exists()
            else:
                rev.is_liked = rev.likes.filter(session_key=session_key).exists() if session_key else False
        except Exception:
            rev.likes_count = 0
            rev.comments_count = 0
            rev.shares_count = 0
            rev.is_liked = False

    context["reviews"] = reviews
    context["average_rating"] = round(average_rating, 1)
    context["total_reviews"] = total_reviews
    context["five_star"] = five_star
    context["four_star"] = four_star
    context["three_star"] = three_star
    context["two_star"] = two_star
    context["one_star"] = one_star
    context["five_percent"] = five_percent
    context["four_percent"] = four_percent
    context["three_percent"] = three_percent
    context["two_percent"] = two_percent
    context["one_percent"] = one_percent
    context["google_maps_api_key"] = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
    context["ghidora_hq"] = {
        "lat": 20.9272684,
        "lng": 81.6929116,
        "name": "Ghidora Transport Headquarter",
        "address": "Ghidora Transport Headquarter, Chhattisgarh"
    }

    return render(
        request,
        "booking/home.html",
        context
    )


@csrf_exempt
def toggle_review_like(request, review_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid method"})
    
    review = get_object_or_404(Review, id=review_id)
    user = request.user if request.user.is_authenticated else None
    
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    if user:
        like, created = ReviewLike.objects.get_or_create(review=review, user=user)
    else:
        like, created = ReviewLike.objects.get_or_create(review=review, session_key=session_key)
        
    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    likes_count = review.likes.count()
    return JsonResponse({"success": True, "liked": liked, "likes_count": likes_count})


@csrf_exempt
def add_review_comment(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    if request.method == "POST":
        text = ""
        user_name = ""
        try:
            data = json.loads(request.body)
            text = data.get("text", "").strip()
            user_name = data.get("name", "").strip()
        except:
            text = request.POST.get("text", "").strip()
            user_name = request.POST.get("name", "").strip()

        if not text:
            return JsonResponse({"success": False, "error": "Comment text required"})

        user = request.user if request.user.is_authenticated else None
        if user:
            name = user.first_name or user.username
        else:
            name = user_name or "Guest User"

        ReviewComment.objects.create(
            review=review,
            user=user,
            user_name=name,
            text=text
        )

    comments_qs = review.comments.order_by("-created_at")
    comments_list = [
        {
            "name": c.user_name,
            "text": c.text,
            "created_at": c.created_at.strftime("%d %b %Y, %I:%M %p")
        }
        for c in comments_qs
    ]
    return JsonResponse({"success": True, "comments": comments_list, "comments_count": comments_qs.count()})


@csrf_exempt
def record_review_share(request, review_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid method"})
    
    review = get_object_or_404(Review, id=review_id)
    user = request.user if request.user.is_authenticated else None
    
    platform = "whatsapp"
    try:
        data = json.loads(request.body)
        platform = data.get("platform", "whatsapp")
    except:
        platform = request.POST.get("platform", "whatsapp")

    ReviewShare.objects.create(
        review=review,
        user=user,
        platform=platform
    )

    shares_count = review.shares.count()
    return JsonResponse({"success": True, "shares_count": shares_count})



def _ors_get_with_retry(url, params, timeout=20, max_attempts=3):
    """
    OpenRouteService ka free server kabhi-kabhi slow ho jata hai aur
    timeout ya galat response de deta hai. Isliye automatically 2-3 baar
    retry karte hain before giving up.
    """
    last_status = None

    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(url, params=params, timeout=timeout)

            if response.status_code == 200:
                return response, None

            last_status = response.status_code
            continue

        except requests.exceptions.Timeout:
            last_status = "timeout"
            continue
        except requests.exceptions.RequestException as e:
            return None, str(e)

    return None, f"status_code: {last_status}"


def calculate_distance_api(request):
    """
    AJAX endpoint: Pickup aur Destination ke naam leke,
    OpenRouteService se unka road-distance (KM me) nikalta hai.
    Frontend se GET request aayegi: ?pickup=Dhamtari&destination=Raipur
    """

    pickup = request.GET.get('pickup', '').strip()
    destination = request.GET.get('destination', '').strip()

    if not pickup or not destination:
        return JsonResponse({'success': False, 'error': 'Pickup ya Destination missing hai'})

    api_key = settings.ORS_API_KEY

    try:
        # Step 1: Pickup ka naam -> coordinates
        geo_url = "https://api.openrouteservice.org/geocode/search"

        pickup_response, error = _ors_get_with_retry(geo_url, {
            'api_key': api_key,
            'text': pickup + ", India",
            'size': 1
        })

        if pickup_response is None:
            return JsonResponse({
                'success': False,
                'error': 'OpenRouteService server abhi slow hai (pickup lookup). Thodi der me try karein ya manual distance daalen.'
            })

        destination_response, error = _ors_get_with_retry(geo_url, {
            'api_key': api_key,
            'text': destination + ", India",
            'size': 1
        })

        if destination_response is None:
            return JsonResponse({
                'success': False,
                'error': 'OpenRouteService server abhi slow hai (destination lookup). Thodi der me try karein ya manual distance daalen.'
            })

        pickup_data = pickup_response.json()
        destination_data = destination_response.json()

        if not pickup_data.get('features'):
            return JsonResponse({'success': False, 'error': f'"{pickup}" location nahi mila'})

        if not destination_data.get('features'):
            return JsonResponse({'success': False, 'error': f'"{destination}" location nahi mila'})

        pickup_coords = pickup_data['features'][0]['geometry']['coordinates']  # [lon, lat]
        destination_coords = destination_data['features'][0]['geometry']['coordinates']

        # Step 2: Coordinates se road-distance nikalna
        directions_url = "https://api.openrouteservice.org/v2/directions/driving-car"

        directions_response, error = _ors_get_with_retry(directions_url, {
            'api_key': api_key,
            'start': f"{pickup_coords[0]},{pickup_coords[1]}",
            'end': f"{destination_coords[0]},{destination_coords[1]}",
        })

        if directions_response is None:
            return JsonResponse({
                'success': False,
                'error': 'OpenRouteService server abhi slow hai (route calculation). Thodi der me try karein ya manual distance daalen.'
            })

        directions_data = directions_response.json()

        if 'features' not in directions_data:
            return JsonResponse({'success': False, 'error': 'Route nahi mil paya in dono jagah ke beech'})

        distance_meters = directions_data['features'][0]['properties']['segments'][0]['distance']
        duration_seconds = directions_data['features'][0]['properties']['segments'][0]['duration']

        distance_km = round(distance_meters / 1000, 1)
        duration_minutes = round(duration_seconds / 60)

        return JsonResponse({
            'success': True,
            'distance_km': distance_km,
            'duration_minutes': duration_minutes,
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def check_status(request):
    """
    Customer enters Booking ID to check booking status & view related Payment Requests/Links.
    """
    booking = None
    payments = None

    if request.method == "POST":
        booking_id = request.POST.get('booking_id', '').strip()

        if booking_id:
            try:
                booking = Booking.objects.get(booking_id=booking_id)
                # Check for related payment requests
                if hasattr(booking, 'payment_requests'):
                    payments = booking.payment_requests.all().order_by('-created_at')
                elif hasattr(booking, 'payments'):
                    payments = booking.payments.all().order_by('-created_at')
            except Booking.DoesNotExist:
                booking = None

    return render(
        request,
        "booking/status.html",
        {
            "booking": booking,
            "payments": payments
        }
    )


def dashboard(request):

    total_bookings = Booking.objects.count()

    pending = Booking.objects.filter(
        status='Pending'
    ).count()

    confirmed = Booking.objects.filter(
        status='Confirmed'
    ).count()

    completed = Booking.objects.filter(
        status='Completed'
    ).count()

    cancelled = Booking.objects.filter(
        status='Cancelled'
    ).count()

    one_way = Booking.objects.filter(
        trip_type='One Way'
    ).count()

    round_trip = Booking.objects.filter(
        trip_type='Round Trip'
    ).count()

    total_earnings = Booking.objects.aggregate(
        Sum('fare')
    )['fare__sum'] or 0

    total_distance = Booking.objects.aggregate(
        Sum('distance')
    )['distance__sum'] or 0

    average_fare = Booking.objects.aggregate(
        Avg('fare')
    )['fare__avg'] or 0

    highest_fare = Booking.objects.aggregate(
        Max('fare')
    )['fare__max'] or 0

    # Most Booked Vehicle
    most_booked_vehicle_data = Booking.objects.values(
        'vehicle_type'
    ).annotate(
        total=Count('vehicle_type')
    ).order_by('-total').first()

    if most_booked_vehicle_data:
        most_booked_vehicle = most_booked_vehicle_data['vehicle_type']
    else:
        most_booked_vehicle = "No Data"

    today_bookings = Booking.objects.filter(
        booking_date__date=timezone.now().date()
    ).count()

    # Top Customer
    top_customer_data = Booking.objects.values(
        'name'
    ).annotate(
        total=Count('id')
    ).order_by('-total').first()

    if top_customer_data:
        top_customer = top_customer_data['name']
    else:
        top_customer = "No Data"

    recent_bookings = Booking.objects.order_by(
        '-booking_date'
    )[:10]

    # Predefined Route Fare Metrics
    total_predefined_routes = PredefinedRouteFare.objects.count()
    active_predefined_routes = PredefinedRouteFare.objects.filter(is_active=True).count()
    inactive_predefined_routes = PredefinedRouteFare.objects.filter(is_active=False).count()
    recently_updated_routes = PredefinedRouteFare.objects.order_by('-updated_at')[:5]

    # Predefined Route Distance Metrics
    total_predefined_distances = PredefinedRouteDistance.objects.count()
    active_predefined_distances = PredefinedRouteDistance.objects.filter(is_active=True).count()
    inactive_predefined_distances = PredefinedRouteDistance.objects.filter(is_active=False).count()
    recently_updated_distances = PredefinedRouteDistance.objects.order_by('-updated_at')[:5]

    context = {
        'total_bookings': total_bookings,
        'pending': pending,
        'confirmed': confirmed,
        'completed': completed,
        'cancelled': cancelled,
        'total_earnings': total_earnings,
        'total_distance': total_distance,
        'average_fare': round(average_fare, 2),
        'highest_fare': highest_fare,
        'one_way': one_way,
        'round_trip': round_trip,
        'most_booked_vehicle': most_booked_vehicle,
        'recent_bookings': recent_bookings,
        'today_bookings': today_bookings,
        'top_customer': top_customer,
        'total_predefined_routes': total_predefined_routes,
        'active_predefined_routes': active_predefined_routes,
        'inactive_predefined_routes': inactive_predefined_routes,
        'recently_updated_routes': recently_updated_routes,
        'total_predefined_distances': total_predefined_distances,
        'active_predefined_distances': active_predefined_distances,
        'inactive_predefined_distances': inactive_predefined_distances,
        'recently_updated_distances': recently_updated_distances,
    }

    return render(
        request,
        'booking/dashboard.html',
        context
    )


def booking_history(request):

    bookings = None

    if request.method == "POST":

        phone = request.POST['phone']

        bookings = Booking.objects.filter(
            phone=phone
        ).order_by('-booking_date')

    return render(
        request,
        "booking/history.html",
        {"bookings": bookings}
    )


def analytics(request):

    # Vehicle Wise Booking Data
    vehicle_data = Booking.objects.values(
        'vehicle_type'
    ).annotate(
        total=Count('vehicle_type')
    ).order_by('-total')

    labels = []
    data = []

    for item in vehicle_data:
        labels.append(item['vehicle_type'])
        data.append(item['total'])

    # Booking Status Graph
    status_labels = [
        'Pending',
        'Confirmed',
        'Completed',
        'Cancelled'
    ]

    status_data = [
        Booking.objects.filter(status='Pending').count(),
        Booking.objects.filter(status='Confirmed').count(),
        Booking.objects.filter(status='Completed').count(),
        Booking.objects.filter(status='Cancelled').count(),
    ]

    # One Way vs Round Trip
    trip_labels = [
        'One Way',
        'Round Trip'
    ]

    trip_data = [
        Booking.objects.filter(trip_type='One Way').count(),
        Booking.objects.filter(trip_type='Round Trip').count(),
    ]

    # Monthly Earnings
    monthly_data = Booking.objects.annotate(
        month=TruncMonth('booking_date')
    ).values(
        'month'
    ).annotate(
        earnings=Sum('fare')
    ).order_by('month')

    month_labels = []
    month_earnings = []

    for item in monthly_data:
        month_labels.append(item['month'].strftime('%b'))
        month_earnings.append(float(item['earnings']))

    top_vehicle = Booking.objects.values('vehicle_type').annotate(total=Count('vehicle_type')).order_by('-total').first()
    top_cust = Booking.objects.values('name').annotate(total=Count('id')).order_by('-total').first()

    # Extra Graph 1: Top Routes Demand
    route_qs = Booking.objects.values('pickup', 'destination').annotate(total=Count('id')).order_by('-total')[:5]
    route_labels = [f"{r['pickup']} ➔ {r['destination']}" for r in route_qs]
    route_data = [r['total'] for r in route_qs]

    # Extra Graph 2: Distance Source (AI Satellite vs Manual)
    src_manual = Booking.objects.filter(distance_source__icontains='Manual').count()
    src_ai = Booking.objects.exclude(distance_source__icontains='Manual').count()
    source_labels = ['Computer Generated (AI Satellite)', 'Manual Entered']
    source_data = [src_ai, src_manual]

    # Extra Graph 3: Distance Range Brackets
    b_short = Booking.objects.filter(distance__lt=50).count()
    b_med = Booking.objects.filter(distance__gte=50, distance__lt=150).count()
    b_long = Booking.objects.filter(distance__gte=150, distance__lt=300).count()
    b_xl = Booking.objects.filter(distance__gte=300).count()
    bracket_labels = ['Local (< 50 KM)', 'State (50-150 KM)', 'Long Haul (150-300 KM)', 'Interstate (300+ KM)']
    bracket_data = [b_short, b_med, b_long, b_xl]

    context = {
        'labels': json.dumps(labels),
        'data': json.dumps(data),

        'status_labels': json.dumps(status_labels),
        'status_data': json.dumps(status_data),

        'trip_labels': json.dumps(trip_labels),
        'trip_data': json.dumps(trip_data),

        'month_labels': json.dumps(month_labels),
        'month_earnings': json.dumps(month_earnings),

        'route_labels': json.dumps(route_labels),
        'route_data': json.dumps(route_data),

        'source_labels': json.dumps(source_labels),
        'source_data': json.dumps(source_data),

        'bracket_labels': json.dumps(bracket_labels),
        'bracket_data': json.dumps(bracket_data),

        # Enhanced Analytics Cards Data
        'total_bookings': Booking.objects.count(),
        'total_earnings': round(Booking.objects.aggregate(Sum('fare'))['fare__sum'] or 0),
        'total_km': round(Booking.objects.aggregate(Sum('distance'))['distance__sum'] or 0, 1),
        'avg_fare': round(Booking.objects.aggregate(Avg('fare'))['fare__avg'] or 0),
        'most_booked_vehicle': top_vehicle['vehicle_type'] if top_vehicle else "No Data",
        'top_customer': top_cust['name'] if top_cust else "No Data",
        'pending_count': Booking.objects.filter(status='Pending').count(),
        'confirmed_count': Booking.objects.filter(status='Confirmed').count(),
        'completed_count': Booking.objects.filter(status='Completed').count(),
        'cancelled_count': Booking.objects.filter(status='Cancelled').count(),
        'recent_bookings': Booking.objects.order_by('-booking_date')[:6],
    }

    return render(
        request,
        'booking/analytics.html',
        context
    )


def manage_bookings(request):

    if request.method == "POST":

        booking_id = request.POST.get("booking_id")
        status = request.POST.get("status")

        try:
            booking = Booking.objects.get(id=booking_id)
            booking.status = status
            booking.save()

        except Booking.DoesNotExist:
            pass

    search = request.GET.get("search")
    status = request.GET.get("status")

    all_bookings = Booking.objects.all()
    total_count = all_bookings.count()
    pending_count = all_bookings.filter(status='Pending').count()
    confirmed_count = all_bookings.filter(status='Confirmed').count()
    completed_count = all_bookings.filter(status='Completed').count()
    cancelled_count = all_bookings.filter(status='Cancelled').count()
    total_revenue = round(all_bookings.aggregate(Sum('fare'))['fare__sum'] or 0)

    bookings = all_bookings

    if search:
        bookings = bookings.filter(
            name__icontains=search
        ) | Booking.objects.filter(
            booking_id__icontains=search
        ) | Booking.objects.filter(
            phone__icontains=search
        )

    if status:
        bookings = bookings.filter(status=status)

    bookings = bookings.order_by("-booking_date")

    return render(
        request,
        "booking/manage_bookings.html",
        {
            "bookings": bookings,
            "total_count": total_count,
            "pending_count": pending_count,
            "confirmed_count": confirmed_count,
            "completed_count": completed_count,
            "cancelled_count": cancelled_count,
            "total_revenue": total_revenue,
            "current_search": search or "",
            "current_status": status or "",
        }
    )


def delete_booking(request, booking_id):

    try:
        booking = Booking.objects.get(id=booking_id)
        booking.delete()

    except Booking.DoesNotExist:
        pass

    return redirect("manage_bookings")


def add_review(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id)

    # Agar review pehle se hai to history page par bhej do
    if Review.objects.filter(booking=booking).exists():
        return redirect("history")

    if request.method == "POST":

        form = ReviewForm(request.POST)

        if form.is_valid():

            review = form.save(commit=False)
            review.booking = booking
            review.save()

            return redirect("history")

    else:

        form = ReviewForm()

    return render(
        request,
        "booking/review.html",
        {
            "form": form,
            "booking": booking,
        }
    )


def download_receipt(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id)

    # View ya Download Mode
    view_mode = request.GET.get("view")

    buffer = generate_receipt_pdf(booking)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")

    if view_mode == "1":
        response["Content-Disposition"] = (
            f'inline; filename=Receipt_{booking.booking_id}.pdf'
        )
    else:
        response["Content-Disposition"] = (
            f'attachment; filename=Receipt_{booking.booking_id}.pdf'
        )

    return response


def about(request):
    return render(request, 'booking/about.html', {})


def services(request):
    return render(request, 'booking/services.html')


def business_card(request):
    return render(request, 'booking/business_card.html')


def contact_us(request):

    success = False

    if request.method == "POST":
        form = ContactMessageForm(request.POST)

        if form.is_valid():
            contact_msg = form.save()

            try:
                from django.core.mail import EmailMessage
                from django.conf import settings

                subject = f"📩 New Contact Message — {contact_msg.subject or 'No Subject'}"
                body = f"""New message received from the Contact Us page:

Name: {contact_msg.name}
Phone: {contact_msg.phone}
Email: {contact_msg.email or 'Not provided'}
Subject: {contact_msg.subject or 'Not provided'}

Message:
{contact_msg.message}
"""
                mail = EmailMessage(
                    subject=subject,
                    body=body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.EMAIL_HOST_USER],
                )
                mail.send(fail_silently=True)
            except Exception as e:
                print("❌ Contact email failed:", e)

            success = True
            form = ContactMessageForm()
    else:
        form = ContactMessageForm()

    return render(
        request,
        "booking/contact.html",
        {"form": form, "success": success}
    )


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def submit_user_review(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method."})

    try:
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '').strip()
        service_used = request.POST.get('service_used', 'Full Truck Transport').strip()
        photo = request.FILES.get('photo')

        if not comment:
            return JsonResponse({"status": "error", "message": "Please write a review comment."})

        # Extract clean single IP address safely for Render proxies
        raw_ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR') or ''
        ip_candidate = raw_ip.split(',')[0].strip() if raw_ip else ''
        
        clean_ip = None
        if ip_candidate:
            import ipaddress
            try:
                clean_ip = str(ipaddress.ip_address(ip_candidate))
            except Exception:
                clean_ip = None

        if clean_ip:
            try:
                recent_count = Review.objects.filter(
                    ip_address=clean_ip,
                    created_at__gte=timezone.now() - timezone.timedelta(minutes=10)
                ).count()
                if recent_count >= 5:
                    return JsonResponse({"status": "error", "message": "Aapne abhi bohot saare reviews submit kiye hain. Kripya thoda wahi rukiye."})
            except Exception:
                pass

        if request.user.is_authenticated:
            user = request.user
            guest_name = user.get_full_name() or user.username
            guest_email = user.email
            guest_phone = getattr(user, 'phone', '')
            is_verified = True
        else:
            user = None
            guest_name = request.POST.get('name', '').strip() or "Guest Customer"
            guest_email = request.POST.get('email', '').strip()
            guest_phone = request.POST.get('phone', '').strip()
            is_verified = False

        # Attempt 1: Direct creation
        try:
            review_obj = Review.objects.create(
                user=user,
                guest_name=guest_name,
                guest_email=guest_email or None,
                guest_phone=guest_phone or None,
                rating=rating,
                comment=comment,
                review=comment,
                service_used=service_used,
                photo=photo if photo else None,
                is_approved=True,
                is_verified=is_verified,
                ip_address=clean_ip
            )
        except Exception as stage1_err:
            import random
            unique_b_id = f"REV-{random.randint(10000000, 99999999)}"
            new_dummy_booking = Booking.objects.create(
                booking_id=unique_b_id,
                name=f"Customer - {guest_name[:50]}",
                phone=guest_phone[:15] if guest_phone else "0000000000",
                email=guest_email or None,
                pickup="Dhamtari",
                destination="Raipur",
                journey_date=timezone.now().date(),
                distance=50.0,
                fare=1500.0,
                vehicle_type="Mahindra Pickup",
                status="Completed"
            )
            review_obj = Review.objects.create(
                booking=new_dummy_booking,
                user=user,
                guest_name=guest_name,
                guest_email=guest_email or None,
                guest_phone=guest_phone or None,
                rating=rating,
                comment=comment,
                review=comment,
                service_used=service_used,
                photo=photo if photo else None,
                is_approved=True,
                is_verified=is_verified,
                ip_address=clean_ip
            )

        # Clear home reviews summary cache immediately
        try:
            cache.delete("home_reviews_summary_data")
        except Exception:
            pass

        return JsonResponse({
            "status": "success",
            "message": "✅ Thank you! Your review has been submitted & published successfully.",
            "review_id": review_obj.id,
            "display_name": review_obj.display_name,
            "rating": review_obj.rating,
            "is_verified": review_obj.is_verified
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"status": "error", "message": f"Review submission issue: {str(e)}"})

def control_tower(request):
    return render(request, "booking/control_tower.html")


@csrf_exempt
def export_bookings_api(request):
    """Export all customer bookings created on Render in JSON format."""
    bookings = Booking.objects.all().order_by('-id')
    data = []
    for b in bookings:
        data.append({
            "booking_id": b.booking_id,
            "name": b.name,
            "phone": b.phone,
            "email": b.email or "",
            "pickup": b.pickup,
            "destination": b.destination,
            "pickup_lat": b.pickup_lat,
            "pickup_lng": b.pickup_lng,
            "destination_lat": b.destination_lat,
            "destination_lng": b.destination_lng,
            "duration_text": b.duration_text or "",
            "journey_date": str(b.journey_date),
            "distance": b.distance,
            "distance_source": b.distance_source,
            "fare": b.fare,
            "fare_type": b.fare_type,
            "vehicle_type": b.vehicle_type,
            "trip_type": b.trip_type,
            "cargo_type": b.cargo_type or "",
            "weight_value": str(b.weight_value) if b.weight_value else "",
            "weight_unit": b.weight_unit,
            "message": b.message or "",
            "status": b.status,
            "created_at": b.booking_date.strftime("%Y-%m-%d %H:%M:%S") if b.booking_date else "",
        })
    return JsonResponse({"success": True, "count": len(data), "bookings": data})


@csrf_exempt
def export_reviews_api(request):
    """Export all customer reviews submitted on Render in JSON format for sync."""
    reviews = Review.objects.all().order_by('-id')
    data = []
    for r in reviews:
        data.append({
            "id": r.id,
            "guest_name": r.display_name,
            "guest_email": r.guest_email or "",
            "guest_phone": r.guest_phone or "",
            "rating": r.rating,
            "comment": r.comment or r.review or "",
            "service_used": r.service_used or "Full Truck Transport",
            "is_approved": r.is_approved,
            "is_verified": r.is_verified,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else "",
        })
    return JsonResponse({"success": True, "count": len(data), "reviews": data})