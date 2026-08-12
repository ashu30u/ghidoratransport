import os
import json
import urllib.request
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghidora_transport.settings')
django.setup()

from booking.models import Booking

RENDER_EXPORT_URL = "https://ghidoratransport.onrender.com/api/export-bookings/"

def sync_bookings_from_render():
    print(f"📡 Fetching live customer bookings from Render: {RENDER_EXPORT_URL} ...")
    try:
        req = urllib.request.Request(
            RENDER_EXPORT_URL,
            headers={'User-Agent': 'GhidoraTransportLocalSync/1.0'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status != 200:
                print(f"❌ Server returned HTTP {response.status}")
                return
            
            payload = json.loads(response.read().decode('utf-8'))
            if not payload.get('success'):
                print("❌ API returned error payload:", payload)
                return
            
            bookings_data = payload.get('bookings', [])
            print(f"📦 Total bookings received from Render: {len(bookings_data)}")
            
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
            
            print(f"✅ SUCCESSFULLY SYNCED! {imported_count} new customer booking(s) imported into Local Database.")
            print(f"📊 Total Bookings in Local Database: {Booking.objects.count()}")

    except Exception as e:
        print("❌ Error syncing bookings from Render:", e)

if __name__ == '__main__':
    sync_bookings_from_render()
