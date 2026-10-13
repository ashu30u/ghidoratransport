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

print("==================================================================")
print("  GHIDORA TRANSPORT - LATEST MOBILE & 2-SIDED PRINT VERIFICATION")
print("==================================================================")

# 1. Feature Strip (Trust Badges 1-Row Grid) in Home Page
print("\n--- 1. Testing Trust Badges in Home Page ---")
resp = client.get(reverse('home'))
assert resp.status_code == 200, f"Home returned {resp.status_code}"
home_html = resp.content.decode('utf-8')

# Check 1-line grid on mobile
assert "grid-template-columns: repeat(4, 1fr) !important;" in home_html, "1-line repeat(4, 1fr) missing in home.html"
assert "font-size: 16px !important;" in home_html, "16px ficon missing in mobile query"
assert "display: none !important;" in home_html, "p display: none missing for mobile trust badge"
print("✓ Trust Badges: Single horizontal line (repeat(4, 1fr)) verified on mobile view!")

# 2. Hamburger Button Across All Templates (Strictly 3 Lines, No 'Menu' Text)
print("\n--- 2. Testing 3-Line Hamburger Button (No 'Menu' Text) Across Templates ---")
templates_to_check = [
    "booking/templates/booking/home.html",
    "booking/templates/booking/base.html",
    "booking/templates/booking/status.html",
    "booking/templates/booking/services.html",
    "booking/templates/booking/contact.html",
    "booking/templates/booking/about.html",
    "booking/templates/booking/business_card.html",
]

for tpl_rel in templates_to_check:
    tpl_path = PROJECT_DIR / tpl_rel
    content = tpl_path.read_text(encoding='utf-8')
    assert "class=\"ham-text\"" not in content, f"Found 'ham-text' class in {tpl_rel}!"
    assert ">Menu<" not in content, f"Found 'Menu' text in {tpl_rel}!"
    assert "<button class=\"hamburger-btn\"" in content or "class=\"hamburger-btn\"" in content, f"hamburger-btn missing in {tpl_rel}!"
    print(f"  ✓ {tpl_rel}: Verified clean 3-line hamburger button without 'Menu' text.")

# 3. AI Weather Radar Comparator & Route Checkpoints
print("\n--- 3. Testing AI Weather Radar Comparator Layout ---")
assert "route-comparator-grid" in home_html, "route-comparator-grid missing in home.html"
assert "route-input-col" in home_html, "route-input-col missing in home.html"
assert "route-btn-col" in home_html, "route-btn-col missing in home.html"
assert "dual-weather-container" in home_html, "dual-weather-container missing in home.html"
assert "Route Weather Checkpoints" in home_html, "Route Weather Checkpoints title missing"
assert "grid-template-columns: 1fr !important;" in home_html, "1-col mobile stacking missing for route comparator"
print("✓ AI Weather Radar: Mobile 1-col responsive stacking and checkpoints verified!")

# 4. Official Instagram URL Update
print("\n--- 4. Testing Official Instagram URL Update ---")
NEW_IG_URL = "https://www.instagram.com/ghidora__transport2286?stkn=c3Q0enVsbzl1dTB6"

resp_contact = client.get(reverse('contact_us'))
assert resp_contact.status_code == 200, f"Contact page returned {resp_contact.status_code}"
contact_html = resp_contact.content.decode('utf-8')
assert NEW_IG_URL in contact_html, "New Instagram URL missing in contact.html"
assert "@ghidora__transport2286" in contact_html, "@ghidora__transport2286 handle missing in contact.html"

# Verify footer and other templates
footer_content = (PROJECT_DIR / "booking/templates/booking/footer.html").read_text(encoding='utf-8')
assert NEW_IG_URL in footer_content, "New Instagram URL missing in footer.html"

base_content = (PROJECT_DIR / "booking/templates/booking/base.html").read_text(encoding='utf-8')
assert NEW_IG_URL in base_content, "New Instagram URL missing in base.html"

about_content = (PROJECT_DIR / "booking/templates/booking/about.html").read_text(encoding='utf-8')
assert NEW_IG_URL in about_content, "New Instagram URL missing in about.html"

# Verify old handles are gone
assert "hamar_kodebod05" not in contact_html
assert "hamar_kodebod05" not in footer_content
assert "hamar_kodebod05" not in base_content
assert "hamar_kodebod05" not in about_content
print("✓ Instagram URL: Successfully updated to @ghidora__transport2286 across all templates!")

# 5. Digital Visiting Card (business_card.html) - Verified Badge & 2-Sided Print
print("\n--- 5. Testing Digital Visiting Card (Verified Badge & 2-Sided Print) ---")
resp_card = client.get(reverse('business_card'))
assert resp_card.status_code == 200, f"Business card returned {resp_card.status_code}"
card_html = resp_card.content.decode('utf-8')

# Check Verified Badge overflow protection
assert "card-verified-badge" in card_html, "card-verified-badge class missing in business_card.html"
assert "back-badge-col" in card_html, "back-badge-col class missing in business_card.html"
assert "flex-shrink: 0" in card_html, "flex-shrink: 0 missing for verified badge"
assert "padding: 16px 14px !important;" in card_html, "Reduced card-face-back mobile padding missing"

# Check 2-Sided Print / PDF feature
assert "SIDE 1: OFFICIAL VEHICLE &amp; TRANSPORT PASS" in card_html, "SIDE 1 print label missing"
assert "SIDE 2: VIP CONTACT CREDENTIALS &amp; QR CODE" in card_html, "SIDE 2 print label missing"
assert "flex-direction: column !important;" in card_html, "flipper-card flex-direction column missing in @media print"
assert "backface-visibility: visible !important;" in card_html, "backface-visibility visible missing in @media print"
assert "transform: none !important;" in card_html, "transform none missing in @media print"
assert "Print Card / PDF (Both Sides)" in card_html, "Print button label missing 'Both Sides'"
print("✓ Digital Visiting Card: Verified badge overflow protection & 2-sided print setup PASSED!")

print("\n==================================================================")
print("  🎉 ALL 5 ENHANCEMENT SUITES PASSED SUCCESSFULLY! ")
print("==================================================================")
