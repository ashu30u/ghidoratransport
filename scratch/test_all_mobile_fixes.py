import os
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to sys.path
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghidora_transport.settings')
django.setup()

from django.test import Client
from django.urls import reverse

client = Client()

print("--- 1. Testing Home Page (/) ---")
resp = client.get(reverse('home'))
assert resp.status_code == 200, f"Home returned {resp.status_code}"
html = resp.content.decode('utf-8')
assert "repeat(2, 1fr)" in html, "Feature strip 2x2 grid not found in home.html"
assert "380px !important" in html, "360 viewer 380px height not found"
assert "padding-bottom: 58px !important" in html, "360 stage padding-bottom not found"
assert "tel:+917489297841" in html, "Call Now +91 7489 297 841 not in home.html"
print("✓ Home page checks PASSED!")

print("\n--- 2. Testing Services Page (/services/) ---")
resp = client.get(reverse('services'))
assert resp.status_code == 200, f"Services returned {resp.status_code}"
html = resp.content.decode('utf-8')
assert "left: 50% !important" in html, "Truck left: 50% not found in services.html"
assert "transform: translate(-50%, -50%) !important" in html, "Truck centering transform not found in services.html"
assert "truck-head-lights" in html, "Headlights not found in services.html"
assert "truck-tail-lights" in html, "Taillights not found in services.html"
assert "touchstart" in html and "touchmove" in html, "Touch events for mobile lights not found in services.html"
assert "tel:+917489297841" in html, "Call Now +91 7489 297 841 not in services.html"
print("✓ Services page checks PASSED!")

print("\n--- 3. Testing Contact Us Page (/contact/) ---")
resp = client.get(reverse('contact_us'))
assert resp.status_code == 200, f"Contact returned {resp.status_code}"
html = resp.content.decode('utf-8')
assert "https://www.instagram.com/reel/DdYPyV7NX0a/?stkn=MWUwcjdhcHhzajk2aw==" in html, "Instagram reel link missing in contact.html"
assert "Instagram Official" in html, "Instagram Official card missing in contact.html"
assert "tel:+917489297841" in html, "tel:+917489297841 missing in contact.html"
print("✓ Contact Us checks PASSED!")

print("\n--- 4. Testing Social Feed Page (/social/) ---")
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.first()
if not user:
    user = User.objects.create_user(username='testverifier', password='testpassword123')
client.force_login(user)

resp = client.get(reverse('social:feed'))
assert resp.status_code == 200, f"Social feed returned {resp.status_code}"
html = resp.content.decode('utf-8')
assert "openCreateReelModal()" in html, "openCreateReelModal() missing in feed.html"
assert "createReelModal" in html, "createReelModal not rendered on feed.html"
print("✓ Social feed checks PASSED!")

print("\n--- 5. Testing Social CSS Mobile Topbar ---")
css_path = os.path.join("social", "static", "social", "css", "social.css")
with open(css_path, "r", encoding="utf-8") as f:
    css_content = f.read()
assert ".gs-social-topbar" in css_content
assert "@media (max-width: 768px)" in css_content
assert ".gs-topbar-search" in css_content
print("✓ Social CSS mobile topbar rules verified!")

print("\n--- 6. Testing Payment Disclaimer ---")
tpl1_path = os.path.join("payments", "templates", "payments", "customer_request_payment.html")
with open(tpl1_path, "r", encoding="utf-8") as f:
    tpl1_content = f.read()
assert "टोल टैक्स (Toll Tax), पार्किंग (Parking)" in tpl1_content, "Toll/Parking disclaimer missing in customer_request_payment.html"
assert "toll-parking-notice" in tpl1_content

tpl2_path = os.path.join("payments", "templates", "payments", "customer_payment_page.html")
with open(tpl2_path, "r", encoding="utf-8") as f:
    tpl2_content = f.read()
assert "टोल टैक्स (Toll Tax), पार्किंग (Parking)" in tpl2_content, "Toll/Parking disclaimer missing in customer_payment_page.html"
print("✓ Payment disclaimers verified on both payment templates!")

print("\n--- 7. Testing Other Pages Call Now Numbers ---")
for tpl, name in [
    ("booking/templates/booking/about.html", "about"),
    ("booking/templates/booking/business_card.html", "business_card"),
    ("booking/templates/booking/base.html", "base"),
    ("booking/templates/booking/status.html", "status"),
]:
    with open(tpl, "r", encoding="utf-8") as f:
        c = f.read()
    assert "tel:+917489297841" in c, f"tel:+917489297841 missing in {tpl}"
    print(f"✓ {name} has updated phone number!")

print("\n==========================================")
print("🎉 ALL 7 REQUIREMENTS VERIFIED 100% SUCCESSFULLY!")
print("==========================================")
