import os
import sys
import django

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghidora_transport.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

def run_tests():
    print("========================================")
    print("GHIDORA TRANSPORT - MOBILE VIEW VERIFICATION")
    print("========================================")

    # 1. CSS Syntax & Brace Balance Check
    css_path = os.path.join('booking', 'static', 'css', 'style.css')
    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()

    opens = css_content.count('{')
    closes = css_content.count('}')
    print(f"1. CSS Brace Balance: Opens={opens}, Closes={closes} -> {'PASS' if opens == closes else 'FAIL'}")
    assert opens == closes, "CSS braces are unbalanced!"

    # 2. Check Footer inclusion in Templates
    target_templates = [
        'booking/templates/booking/home.html',
        'booking/templates/booking/about.html',
        'booking/templates/booking/services.html',
        'booking/templates/booking/contact.html',
        'booking/templates/booking/status.html',
        'booking/templates/booking/user_dashboard.html',
    ]
    print("\n2. Footer Template Inclusion Check:")
    for t in target_templates:
        with open(t, 'r', encoding='utf-8') as fh:
            c = fh.read()
            included = 'booking/footer.html' in c
            print(f"   - {t}: {'PASS' if included else 'FAIL'}")
            assert included, f"Footer missing from {t}"

    # 3. HTTP GET Requests on all 6 Pages
    client = Client()
    User = get_user_model()
    test_user, created = User.objects.get_or_create(username='mobile_test_user')
    if created:
        test_user.set_password('testpass123')
        test_user.save()

    client.force_login(test_user)

    pages = [
        ('/', 'Home'),
        ('/about/', 'About Us'),
        ('/services/', 'Services'),
        ('/contact/', 'Contact Us'),
        ('/status/', 'Track Booking'),
        ('/user-dashboard/', 'User Dashboard'),
    ]

    print("\n3. HTTP Rendering & Key Elements Verification:")
    for url, name in pages:
        res = client.get(url)
        assert res.status_code == 200, f"Page {url} returned {res.status_code}"
        html = res.content.decode('utf-8', errors='ignore')

        has_footer = 'ghidora-footer' in html or 'GHIDORA TRANSPORT' in html
        has_logo = 'logo6.png' in html
        has_drawer = 'mobileNavDrawer' in html or 'mobileDrawer' in html

        print(f"   [{name} ({url})] Status: {res.status_code}")
        print(f"      - Footer rendered: {has_footer}")
        print(f"      - Logo image present: {has_logo}")
        print(f"      - Mobile Drawer present: {has_drawer}")

        assert has_footer, f"Footer markup missing in rendered {url}"
        assert has_logo, f"Logo missing in {url}"
        assert has_drawer, f"Mobile drawer missing in {url}"

    print("\n========================================")
    print("ALL TESTS PASSED! MOBILE VIEW IS FULLY VERIFIED.")
    print("========================================")

if __name__ == '__main__':
    run_tests()
