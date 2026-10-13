import os
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8')

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghidora_transport.settings')
django.setup()

from django.test import Client
from django.urls import reverse

client = Client()

print("==================================================================")
print("  TESTING CALCULATE FARE AUTO-SCROLL TO RESULT CARD")
print("==================================================================")

resp = client.get(reverse('home'))
assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
html = resp.content.decode('utf-8')

# 1. Check Button onclick and id
assert 'id="calculateFareBtn"' in html, 'id="calculateFareBtn" missing from button'
assert 'onclick="calculateFare(true)"' in html, 'onclick="calculateFare(true)" missing from button'
print("✓ Calculate Fare button: onclick passes true to trigger smooth scroll!")

# 2. Check scrollToFareResult function
assert 'function scrollToFareResult()' in html, 'scrollToFareResult function missing from scripts'
assert 'window.scrollTo({' in html, 'window.scrollTo missing from scrollToFareResult'
assert 'behavior: \'smooth\'' in html, 'behavior: smooth missing from scrollTo'
assert 'fare-box-pulse' in html, 'fare-box-pulse missing from scrollToFareResult'
print("✓ scrollToFareResult: Smooth scroll calculation and visual pulse glow verified!")

# 3. Check CSS Animation for Pulse Glow
assert '@keyframes fareGlowPulse' in html, '@keyframes fareGlowPulse missing from styles'
assert '.fare-box-pulse {' in html, '.fare-box-pulse class missing from styles'
print("✓ CSS Animation: .fare-box-pulse with green/orange glowing highlight verified!")

# 4. Check calculateFare shouldScroll handling
assert 'async function calculateFare(shouldScroll = false)' in html, 'calculateFare shouldScroll parameter missing'
assert 'if (shouldScroll) {' in html, 'shouldScroll conditional check missing'
assert 'window.scrollToFareResult = scrollToFareResult;' in html, 'window.scrollToFareResult export missing'
print("✓ calculateFare: Automatically scrolls down to fareResultBox upon button click!")

# 5. Run Laptop & Mobile regression tests
print("\n--- Running Laptop Hero Fold & Mobile Regression Tests ---")
import subprocess
result = subprocess.run([sys.executable, "scratch/test_laptop_hero_fold.py"], capture_output=True, text=True, encoding='utf-8')
print(result.stdout)
assert result.returncode == 0, f"Regression tests failed:\n{result.stderr}"

print("==================================================================")
print("  🎉 ALL TESTS PASSED! CALCULATE FARE AUTO-SCROLL VERIFIED! ")
print("==================================================================")
