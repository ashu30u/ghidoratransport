import os
import json

import requests

from django.conf import settings
from django.core.mail import EmailMessage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Avg, Max, Count
from django.db.models.functions import TruncMonth
from django.template.loader import get_template
from django.utils import timezone

from .models import Booking, Review
from .forms import ReviewForm
from .utils import generate_receipt_pdf
from drivers.views import auto_assign_driver_to_booking


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


def home(request):

    context = {}
    reviews = Review.objects.all().order_by("-created_at")

    average_rating = Review.objects.aggregate(
    Avg("rating")
    )["rating__avg"] or 0

    total_reviews = Review.objects.count()

    five_star = Review.objects.filter(rating=5).count()
    four_star = Review.objects.filter(rating=4).count()
    three_star = Review.objects.filter(rating=3).count()
    two_star = Review.objects.filter(rating=2).count()
    one_star = Review.objects.filter(rating=1).count()

    if request.method == "POST":

        name = request.POST['name']
        phone = request.POST['phone']
        email = request.POST.get('email', '').strip()
        pickup = request.POST['pickup']
        destination = request.POST['destination']
        journey_date = request.POST['journey_date']
        distance = float(request.POST['distance'])
        vehicle_type = request.POST['vehicle_type']
        trip_type = request.POST['trip_type']

        # Frontend se aayega: "Google Generated" ya "Manual Entered".
        # Agar kisi wajah se na aaye, default "Manual Entered" maan lo.
        distance_source = request.POST.get('distance_source', 'Manual Entered')

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

        if trip_type == "Round Trip":
            distance = distance * 2

        fare = distance * rate

        booking = Booking.objects.create(
            name=name,
            phone=phone,
            email=email if email else None,
            pickup=pickup,
            destination=destination,
            journey_date=journey_date,
            distance=distance,
            distance_source=distance_source,
            fare=fare,
            vehicle_type=vehicle_type,
            trip_type=trip_type
        )
        auto_assign_driver_to_booking(booking)
        # Email ab yahan nahi bhejte -- Booking model ke post_save signal
        # (models.py) status "Completed" hone par khud email bhej dega.

        context = {
            "success": True,
            "booking_id": booking.booking_id,
            "status": booking.status,
            "name": name,
            "phone": phone,
            "pickup": pickup,
            "destination": destination,
            "journey_date": journey_date,
            "distance": distance,
            "fare": fare,
            "vehicle_type": vehicle_type,
            "trip_type": trip_type
        }

    reviews = Review.objects.all().order_by("-created_at")[:6]


    context["reviews"] = reviews
    context["average_rating"] = round(average_rating, 1)
    context["total_reviews"] = total_reviews
    context["five_star"] = five_star
    context["four_star"] = four_star
    context["three_star"] = three_star
    context["two_star"] = two_star
    context["one_star"] = one_star

    return render(
        request,
        "booking/home.html",
        context
    )


def check_status(request):

    booking = None

    if request.method == "POST":

        booking_id = request.POST['booking_id']

        try:
            booking = Booking.objects.get(
                booking_id=booking_id
            )

        except Booking.DoesNotExist:
            booking = None

    return render(
        request,
        "booking/status.html",
        {"booking": booking}
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

        labels.append(
            item['vehicle_type']
        )

        data.append(
            item['total']
        )

    # Booking Status Graph

    status_labels = [
        'Pending',
        'Confirmed',
        'Completed',
        'Cancelled'
    ]

    status_data = [
        Booking.objects.filter(
            status='Pending'
        ).count(),

        Booking.objects.filter(
            status='Confirmed'
        ).count(),

        Booking.objects.filter(
            status='Completed'
        ).count(),

        Booking.objects.filter(
            status='Cancelled'
        ).count(),
    ]

    # One Way vs Round Trip

    trip_labels = [
        'One Way',
        'Round Trip'
    ]

    trip_data = [
        Booking.objects.filter(
            trip_type='One Way'
        ).count(),

        Booking.objects.filter(
            trip_type='Round Trip'
        ).count(),
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

        month_labels.append(
            item['month'].strftime('%b')
        )

        month_earnings.append(
            float(item['earnings'])
        )


    context = {

    'labels': json.dumps(labels),
    'data': json.dumps(data),

    'status_labels': json.dumps(status_labels),
    'status_data': json.dumps(status_data),

    'trip_labels': json.dumps(trip_labels),
    'trip_data': json.dumps(trip_data),

    'month_labels': json.dumps(month_labels),
    'month_earnings': json.dumps(month_earnings),

    # Analytics Cards Data

    'total_bookings': Booking.objects.count(),

    'total_earnings':
    Booking.objects.aggregate(
        Sum('fare')
    )['fare__sum'] or 0,

    'most_booked_vehicle':
    Booking.objects.values(
        'vehicle_type'
    ).annotate(
        total=Count('vehicle_type')
    ).order_by('-total').first()['vehicle_type'],

    'top_customer':
    Booking.objects.values(
        'name'
    ).annotate(
        total=Count('id')
    ).order_by('-total').first()['name'],
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

    bookings = Booking.objects.all()

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
            "bookings": bookings
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