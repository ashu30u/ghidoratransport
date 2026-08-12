import os
import json
import urllib.request
import warnings
warnings.filterwarnings('ignore')

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghidora_transport.settings')
django.setup()

from booking.models import Booking

RENDER_EXPORT_URL = "https://ghidoratransport.onrender.com/api/export-bookings/"

def sync_bookings_from_render():
    print(f"📡 Connecting to Render Server: {RENDER_EXPORT_URL} ...")
    try:
        req = urllib.request.Request(
            RENDER_EXPORT_URL,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) GhidoraSync/1.0'}
        )
        with urllib.request.urlopen(req, timeout=20) as response:
            if response.status != 200:
                print(f"❌ Server returned HTTP status: {response.status}")
                return

            raw_data = response.read().decode('utf-8')
            payload = json.loads(raw_data)
            
            if not payload.get('success'):
                print("❌ API returned error payload:", payload)
                return

            bookings_data = payload.get('bookings', [])
            print(f"🟢 Connected successfully! Total bookings on Render server: {len(bookings_data)}")

            if len(bookings_data) == 0:
                print("ℹ️ Currently there are 0 customer bookings on Render server. Test by submitting a new booking on https://ghidoratransport.onrender.com !")
                return

            imported_count = 0
            for b in bookings_data:
                booking_id = b.get('booking_id')
                if not booking_id:
                    continue

                existing = Booking.objects.filter(booking_id=booking_id).first()
                if not existing:
                    Booking.objects.create(
                        booking_id=booking_id,
                        name=b.get('name', 'Customer'),
                        phone=b.get('phone', ''),
                        email=b.get('email') or None,
                        pickup=b.get('pickup', ''),
                        destination=b.get('destination', ''),
                        pickup_lat=b.get('pickup_lat'),
                        pickup_lng=b.get('pickup_lng'),
                        destination_lat=b.get('destination_lat'),
                        destination_lng=b.get('destination_lng'),
                        duration_text=b.get('duration_text') or None,
                        journey_date=b.get('journey_date'),
                        distance=float(b.get('distance') or 50),
                        distance_source=b.get('distance_source', 'Manual Entered'),
                        fare=float(b.get('fare') or 0),
                        fare_type=b.get('fare_type', 'Distance Based Fare'),
                        vehicle_type=b.get('vehicle_type', 'Mahindra Pickup'),
                        trip_type=b.get('trip_type', 'One Way'),
                        cargo_type=b.get('cargo_type') or None,
                        weight_value=float(b['weight_value']) if b.get('weight_value') else None,
                        weight_unit=b.get('weight_unit', 'kg'),
                        message=b.get('message') or None,
                        status=b.get('status', 'Pending')
                    )
                    imported_count += 1

            print(f"✅ SUCCESS! {imported_count} new customer booking(s) imported into Localhost database.")
            print(f"📊 Total Bookings in Local Database: {Booking.objects.count()}")

    except urllib.error.HTTPError as he:
        print(f"⚠️ Render server is still restarting/deploying (HTTP {he.code}). Please wait 15 seconds and try again!")
    except Exception as e:
        print("❌ Error syncing bookings from Render:", e)

if __name__ == '__main__':
    sync_bookings_from_render()
