import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghidora_transport.settings')
django.setup()

from booking.models import Booking, Review

def inspect_and_ensure_all_reviews():
    all_reviews = Review.objects.all().select_related('booking')
    print(f"Total Review Count in Database: {all_reviews.count()}")
    
    for r in all_reviews:
        name = r.booking.name if r.booking else "Anonymous"
        print(f"ID: {r.id} | Name: {name} | Rating: {r.rating} | Comment: {r.comment}")

    # Rich default reviews list to make sure site always has full 9 reviews
    full_review_set = [
        ("Reshma Rose", 5, "Had a very good professional experience with Ghidora Transport team. They were always ready for corrections, changes & gave instructions to improve as needed."),
        ("Sanjiv", 4, "Very professional transport service. The booking process was easy and the fare was reasonable. Will definitely use again."),
        ("Nilay Singh", 5, "Good experience. Vehicle was clean and the driver was polite. Delivery was completed without any issues."),
        ("Utkarsh", 4, "Overall experience achha raha. Bas driver 15 minute late aaya tha, baaki sab perfect tha."),
        ("Amit Kumar", 4, "Service theek thi. Driver polite tha lekin location dhundhne me thoda time lag gaya."),
        ("Tarun Sahu", 5, "Bohot badhiya service. Saamaan safely aur time par deliver ho gaya. Highly recommended!"),
        ("Priya Sharma", 5, "Mahindra Pickup booking bohot fast hui. Rate quote exact tha, koi hidden charge nahi tha."),
        ("Rajesh Patel", 5, "Raipur se Dhamtari saamaan bheja tha. Driver ne safe drive kiya aur bina kisi tut-phut ke pahunchaya."),
        ("Ankit Verma", 4, "Best transport service in Chhattisgarh. Live GPS track aur weather alert bohot kaam ka feature hai.")
    ]

    for i, (name, rating, comment) in enumerate(full_review_set):
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
        r, created = Review.objects.get_or_create(
            booking=booking,
            defaults={'rating': rating, 'comment': comment}
        )
        if not created:
            r.rating = rating
            r.comment = comment
            r.save()

    print(f"Final Guaranteed Review Count in DB: {Review.objects.count()}")

if __name__ == '__main__':
    inspect_and_ensure_all_reviews()
