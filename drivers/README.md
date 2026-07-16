# Driver Management App — Ghidora Transport (Django)

## 1. App ko project me daalein
`drivers/` folder ko apne Django project ke root me copy karein
(jahan `manage.py` hai, uske saath).

## 2. `settings.py` me register karein
```python
INSTALLED_APPS = [
    ...
    'drivers',
]

# Agar pehle se nahi hai:
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

Pillow install karein (photo/image upload ke liye):
```
pip install Pillow
```

## 3. Main `urls.py` me include karein
```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    ...
    path('', include('drivers.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## 4. Migrate karein
```
python manage.py makemigrations drivers
python manage.py migrate
```

Ab Django Admin (`/admin/`) me bhi "Drivers" aur "Vehicles" automatically dikhenge
(customized list view, status badges, actions ke saath).

Custom dashboard yahan available hoga: **`/admin-panel/drivers/`**

## 5. Apne Booking model se connect karein

Apne existing `Booking` model me ye field add karein:
```python
assigned_driver = models.ForeignKey(
    'drivers.Driver', null=True, blank=True, on_delete=models.SET_NULL
)
```
Migration chalayein:
```
python manage.py makemigrations
python manage.py migrate
```

Booking create hone ke baad (view ya `save()` me) ye call karein:
```python
from drivers.views import auto_assign_driver_to_booking

booking = Booking.objects.create(...)
auto_assign_driver_to_booking(booking)
```

**Logic:** Jab tak system me sirf ek hi driver hai, wahi automatically har
booking par permanent assign hota rahega (`is_default=True`). Jaise hi admin
naye drivers add karega aur kisi aur ko "Make Default" karega, ya kisi
booking par manually driver change karega, us booking ke liye wahi
assignment lock ho jayegi (auto-assign sirf tab hota hai jab
`assigned_driver` khali ho).

## 6. Customer ki booking-status page par driver dikhana

Apne booking-status template me:
```django
{% include 'drivers/customer_driver_card.html' with driver=booking.assigned_driver %}
```

Isme automatically **📞 Call Driver** aur **💬 WhatsApp Driver** buttons
render honge (`tel:` aur `wa.me` links).

## 7. Admin panel me ek driver ko manually change karna

Har booking ke admin edit page me (agar aap Booking ko Django Admin me register
karte hain), `assigned_driver` field ko admin dropdown se change kiya ja
sakta hai — ya apna khud ka "Assign Booking" view bhi bana sakte hain jo
`drivers/views.py` ke pattern follow kare.

## Design Notes
- Glassmorphism dark theme (`drivers/static/drivers/css/driver.css`) —
  aap apne main website ke color palette se match karne ke liye isko edit
  kar sakte hain.
- Sab templates standalone HTML hain — agar aapka apna base template
  (navbar/footer) hai to `{% extends 'base.html' %}` add kar lein.
