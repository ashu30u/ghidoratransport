import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghidora_transport.settings')
django.setup()

from booking.models import Booking, Review
from django.utils import timezone

def ensure_nine_reviews():
    sample_reviews = [
        ("Reshma Rose", 5, "Had a very good professional experience with Ghidora Transport team. They were always ready for corrections, changes & gave instructions to improve as needed."),
        ("Sanjiv", 4, "Very professional transport service. The booking process was easy and the fare was reasonable. Will definitely use again."),
        ("Nilay Singh", 4, "Good experience. Vehicle was clean and the driver was polite. Delivery was completed without any issues."),
        ("Utkarsh", 4, "Overall experience achha raha. Bas driver 15 minute late aaya tha, baaki sab perfect tha."),
        ("Amit Kumar", 4, "Service theek thi. Driver polite tha lekin location dhundhne me thoda time lag gaya."),
        ("Tarun Sahu", 5, "Bohot badhiya service. Saamaan safely aur time par deliver ho gaya. Highly recommended!"),
        ("Priya Sharma", 5, "Mahindra Pickup booking bohot fast hui. Rate quote exact tha, koi hidden charge nahi tha."),
        ("Rajesh Patel", 5, "Raipur se Dhamtari saamaan bheja tha. Driver ne safe drive kiya aur bina kisi tut-phut ke pahunchaya."),
        ("Ankit Verma", 4, "Best transport service in Chhattisgarh. Live GPS track and weather alert bohot kaam ka feature hai.")
    ]

    current_count = Review.objects.count()
    print(f"Current Review Count in DB: {current_count}")

    if current_count < 9:
        print("Adding sample reviews to reach 9 total customer reviews...")
        for i, (name, rating, comment) in enumerate(sample_reviews):
            booking, _ = Booking.objects.get_or_create(
                name=name,
                phone=f"987654321{i}",
                defaults={
                    'pickup': 'Raipur',
                    'destination': 'Dhamtari',
                    'journey_date': '2026-06-30',
                    'distance': 77.6,
                    'fare': 1550,
                    'status': 'Confirmed'
                }
            )
            review, created = Review.objects.get_or_create(
                booking=booking,
                defaults={
                    'rating': rating,
                    'comment': comment
                }
            )
            if not created:
                review.rating = rating
                review.comment = comment
                review.save()
        print(f"New Review Count in DB: {Review.objects.count()}")
    else:
        print("Database already has 9 or more customer reviews!")

if __name__ == '__main__':
    ensure_nine_reviews()
