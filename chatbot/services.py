"""
chatbot/services.py

Ye asli tools hain jo LLM call karega. Booking model aur distance
calculation hum booking app se hi import kar rahe hain - taaki
duplicate code na ho aur wahi real data use ho.
"""

from django.conf import settings

from booking.models import Booking
from booking.views import _ors_get_with_retry  # same retry helper jo booking app me hai


VEHICLE_RATES = {
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


def _get_distance_km(pickup, destination):
    """booking app ke calculate_distance_api() jaisa hi logic,
    bas JsonResponse ki jagah plain (value, error) return karta hai."""
    api_key = settings.ORS_API_KEY
    geo_url = "https://api.openrouteservice.org/geocode/search"

    pickup_response, _ = _ors_get_with_retry(geo_url, {'api_key': api_key, 'text': pickup + ", India", 'size': 1})
    if pickup_response is None:
        return None, "Distance service abhi slow hai, thodi der me try karein."

    destination_response, _ = _ors_get_with_retry(geo_url, {'api_key': api_key, 'text': destination + ", India", 'size': 1})
    if destination_response is None:
        return None, "Distance service abhi slow hai, thodi der me try karein."

    pickup_data = pickup_response.json()
    destination_data = destination_response.json()

    if not pickup_data.get('features'):
        return None, f'"{pickup}" location nahi mila'
    if not destination_data.get('features'):
        return None, f'"{destination}" location nahi mila'

    pickup_coords = pickup_data['features'][0]['geometry']['coordinates']
    destination_coords = destination_data['features'][0]['geometry']['coordinates']

    directions_url = "https://api.openrouteservice.org/v2/directions/driving-car"
    directions_response, _ = _ors_get_with_retry(directions_url, {
        'api_key': api_key,
        'start': f"{pickup_coords[0]},{pickup_coords[1]}",
        'end': f"{destination_coords[0]},{destination_coords[1]}",
    })
    if directions_response is None:
        return None, "Route calculate nahi ho paaya, thodi der me try karein."

    directions_data = directions_response.json()
    if 'features' not in directions_data:
        return None, "Route nahi mila in dono jagah ke beech"

    distance_meters = directions_data['features'][0]['properties']['segments'][0]['distance']
    return round(distance_meters / 1000, 1), None


def calculate_fare(source: str, destination: str, vehicle_type: str = None) -> dict:
    """Tool: fare estimate calculate karta hai."""
    distance_km, error = _get_distance_km(source, destination)
    if error:
        return {"error": error}

    vt = vehicle_type if vehicle_type in VEHICLE_RATES else "Mahindra Pickup"
    rate = VEHICLE_RATES[vt]
    fare = distance_km * rate

    return {
        "source": source,
        "destination": destination,
        "distance_km": distance_km,
        "vehicle_type_used": vt,
        "estimated_fare": round(fare, 2),
        "note": "Round trip pe fare double hota hai. Vehicle type badalne se fare alag hoga.",
    }


def get_booking_status(booking_id: str) -> dict:
    """Tool: booking status, pickup/destination, aur (agar assigned hai to) driver deta hai."""
    try:
        booking = Booking.objects.get(booking_id=booking_id)
    except Booking.DoesNotExist:
        return {"error": f"Booking ID {booking_id} nahi mila."}

    result = {
        "booking_id": booking.booking_id,
        "status": booking.status,
        "pickup": booking.pickup,
        "destination": booking.destination,
        "vehicle_type": booking.vehicle_type,
    }

    # NOTE: agar Booking model me driver field ka naam alag hai
    # (jaise booking.assigned_driver), yahan wahi naam use karein.
    driver = getattr(booking, "driver", None)
    if driver:
        result["driver_name"] = getattr(driver, "name", None)

    return result


def get_driver_contact(booking_id: str) -> dict:
    """Tool: driver ka phone number deta hai (agar assigned hai)."""
    try:
        booking = Booking.objects.get(booking_id=booking_id)
    except Booking.DoesNotExist:
        return {"error": f"Booking ID {booking_id} nahi mila."}

    driver = getattr(booking, "driver", None)
    if not driver:
        return {"error": "Is booking me abhi tak koi driver assign nahi hua hai."}

    return {
        "driver_name": getattr(driver, "name", "N/A"),
        "phone": getattr(driver, "phone", "N/A"),
    }


def get_services() -> dict:
    """Tool: available services ki static list."""
    return {
        "services": [
            {"name": "Goods Transport", "emoji": "🚚"},
            {"name": "House Shifting", "emoji": "🏠"},
            {"name": "Business Transport", "emoji": "🏢"},
            {"name": "Agriculture Transport", "emoji": "🌾"},
        ]
    }