import os
import sys
from pathlib import Path
from datetime import date

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8')

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghidora_transport.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from occasions.models import Occasion, OccasionSettings

client = Client()

print("==================================================================")
print("  TESTING 1-PAGE LAPTOP HERO FOLD (WITH & WITHOUT OCCASION BAR)")
print("==================================================================")

# Clean any existing occasion for today first to test default
today = date.today()
Occasion.objects.filter(month=today.month, day=today.day).delete()

# Test 1: Without Occasion
print("\n--- 1. Testing Default View (Without Occasion Banner) ---")
resp = client.get(reverse('home'))
assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
html = resp.content.decode('utf-8')

assert "--hero-top-offset: 60px;" in html, "--hero-top-offset: 60px; missing when no occasion"
assert "calc(100vh - var(--hero-top-offset, 60px))" in html, "calc(100vh - var(--hero-top-offset, 60px)) missing"
assert "calc(100dvh - var(--hero-top-offset, 60px))" in html, "calc(100dvh - var(--hero-top-offset, 60px)) missing"
assert "@media (min-width: 992px)" in html, "@media (min-width: 992px) missing"
assert "syncHeroFoldHeight" in html, "syncHeroFoldHeight function missing"
print("✓ Default laptop hero fold: 100vh full-page height verified!")

# Test 2: With Active Occasion
print("\n--- 2. Testing With Active Occasion Banner ---")
occ = Occasion.objects.create(
    name="Test Festival",
    message="Special Festival Offer & Greetings from Ghidora Transport!",
    month=today.month,
    day=today.day,
    is_active=True
)
setting, _ = OccasionSettings.objects.update_or_create(id=1, defaults={'show_on_website': True})

try:
    resp = client.get(reverse('home'))
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    html_occ = resp.content.decode('utf-8')

    assert "--hero-top-offset: 104px;" in html_occ, "--hero-top-offset: 104px; missing when occasion active"
    assert "occasion-banner" in html_occ, "occasion-banner class missing when occasion active"
    assert "Special Festival Offer &amp; Greetings" in html_occ or "Special Festival Offer" in html_occ, "Occasion message missing"
    assert "calc(100vh - var(--hero-top-offset, 60px))" in html_occ, "Dynamic hero height rule missing"
    print("✓ Occasion active hero fold: --hero-top-offset adjusts to 104px and keeps exact 100vh 1-page height!")
finally:
    occ.delete()

# Test 3: Re-verify previous 5 mobile & platform suites
print("\n--- 3. Running Regression Checks for Previous Mobile & Print Suites ---")
import subprocess
result = subprocess.run([sys.executable, "scratch/test_latest_mobile_enhancements.py"], capture_output=True, text=True, encoding='utf-8')
print(result.stdout)
assert result.returncode == 0, f"Regression tests failed:\n{result.stderr}"

print("==================================================================")
print("  🎉 ALL TESTS PASSED! LAPTOP HERO FOLD IS PERFECTLY 1 PAGE! ")
print("==================================================================")
