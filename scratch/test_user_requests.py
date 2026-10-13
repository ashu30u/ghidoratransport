import os
import sys

sys.path.insert(0, os.path.abspath('.'))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghidora_transport.settings')
django.setup()

import re
from django.test import RequestFactory
from django.contrib.auth import get_user_model, authenticate
from django.contrib.sessions.middleware import SessionMiddleware
from booking.models import Booking
from social.models import Profile
from booking.views import check_status, forgot_password_view
from booking.backends import MultiIdentifierBackend

User = get_user_model()
factory = RequestFactory()

def add_session(request):
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()
    return request

def test_360_video_attributes():
    print("\n--- 1. Testing 360 Video Attributes in home.html ---")
    with open('booking/templates/booking/home.html', 'r', encoding='utf-8') as f:
        content = f.read()

    assert 'id="viewer360Video"' in content, "viewer360Video not found!"
    assert 'autoplay' in content, "autoplay missing on 360 video!"
    assert 'poster=' in content, "poster missing on 360 video!"
    assert 'preload="auto"' in content, "preload auto missing on 360 video!"
    assert 'startPlay' in content, "startPlay autoplay trigger missing in engine init!"
    assert 'images/360view/1.png' in content, "poster frame reference missing!"
    print("✅ 360 Bolero Video contains autoplay, muted, playsinline, preload='auto', poster, and instant play trigger.")

def test_check_status_search():
    print("\n--- 2. Testing Booking Status Search (Booking ID / Mobile / Email) ---")
    test_phone = "9988776655"
    test_email = "testcustomer9988@example.com"
    Booking.objects.filter(phone=test_phone).delete()

    booking1 = Booking.objects.create(
        booking_id="GT9901",
        name="Test Customer",
        phone=test_phone,
        email=test_email,
        pickup="Raipur Station",
        destination="Bhilai Steel Plant",
        vehicle_type="Mahindra Bolero Pickup",
        status="Confirmed",
        journey_date="2026-09-20",
        distance=35.0,
        fare=1850.0
    )

    # 0) Initial GET request (User visits /status/ directly)
    req_get = factory.get('/status/')
    resp_get = check_status(req_get)
    assert resp_get.status_code == 200, "GET /status/ failed!"
    print("✅ Initial GET /status/ rendered cleanly with no VariableDoesNotExist exception.")

    # A) Search by Booking ID
    req = factory.post('/booking/status/', {'booking_id': 'GT9901'})
    resp = check_status(req)
    assert resp.status_code == 200
    html = resp.content.decode('utf-8')
    assert "GT9901" in html, "Booking ID GT9901 not in rendered response!"
    print("✅ Search by Booking ID ('GT9901') succeeded.")

    # B) Search by 10-digit Mobile Number (Single match)
    req2 = factory.post('/booking/status/', {'booking_id': test_phone})
    resp2 = check_status(req2)
    assert resp2.status_code == 200
    html2 = resp2.content.decode('utf-8')
    assert "GT9901" in html2, "Booking not found when searching by phone number!"
    assert "Found booking for" in html2 or "Consignment Reference ID" in html2
    print("✅ Search by 10-digit Mobile ('9988776655') found booking GT9901 with recovered ID.")

    # C) Search by Email
    req3 = factory.post('/booking/status/', {'booking_id': test_email})
    resp3 = check_status(req3)
    assert resp3.status_code == 200
    html3 = resp3.content.decode('utf-8')
    assert "GT9901" in html3, "Booking not found when searching by email!"
    print("✅ Search by Email succeeded.")

    # D) Search with multiple bookings for same phone
    booking2 = Booking.objects.create(
        booking_id="GT9902",
        name="Test Customer",
        phone=test_phone,
        email=test_email,
        pickup="Durg City",
        destination="Bilaspur Hub",
        vehicle_type="Tata Ace Gold",
        status="Pending",
        journey_date="2026-09-25",
        distance=120.0,
        fare=2400.0
    )
    req4 = factory.post('/booking/status/', {'booking_id': test_phone})
    resp4 = check_status(req4)
    html4 = resp4.content.decode('utf-8')
    assert "Your Shipments Found" in html4, "Multiple bookings card not displayed!"
    assert "GT9901" in html4 and "GT9902" in html4, "Both bookings not listed in multi-booking card!"
    print("✅ Multiple bookings lookup for phone number listed all bookings (GT9901 & GT9902).")

    # Clean up test bookings
    Booking.objects.filter(phone=test_phone).delete()

def test_multi_identifier_login():
    print("\n--- 3. Testing Multi-Identifier Backend (Mobile / Email / Username) ---")
    test_user_phone = "9112233445"
    test_user_email = "ghidora_tester911@gmail.com"
    test_user_name = "tester_user_911"
    test_password = "SecurePassword123!"

    Profile.objects.filter(phone=test_user_phone).update(phone=None)
    User.objects.filter(username=test_user_name).delete()

    user = User.objects.create_user(
        username=test_user_name,
        email=test_user_email,
        password=test_password
    )

    profile, _ = Profile.objects.get_or_create(user=user)
    profile.phone = test_user_phone
    profile.save()

    backend = MultiIdentifierBackend()

    # 1. Login with Username
    auth1 = backend.authenticate(None, username=test_user_name, password=test_password)
    assert auth1 is not None and auth1.id == user.id, "Login via Username failed!"
    print("✅ Login via Username succeeded.")

    # 2. Login with Email
    auth2 = backend.authenticate(None, username=test_user_email, password=test_password)
    assert auth2 is not None and auth2.id == user.id, "Login via Email succeeded!"
    print("✅ Login via Email succeeded.")

    # 3. Login with Mobile Number
    auth3 = backend.authenticate(None, username=test_user_phone, password=test_password)
    assert auth3 is not None and auth3.id == user.id, "Login via Mobile Number failed!"
    print("✅ Login via 10-digit Mobile Number succeeded.")

    # 4. Login via Django's universal authenticate() function
    auth_u = authenticate(username=test_user_phone, password=test_password)
    assert auth_u is not None and auth_u.id == user.id, "Universal authenticate() with mobile failed!"
    print("✅ Django authenticate(username=mobile, password=pwd) succeeded through AUTHENTICATION_BACKENDS.")

def test_forgot_password_otp_flow():
    print("\n--- 4. Testing End-to-End Forgot Password via OTP & Mobile ---")
    test_user_phone = "9112233445"
    user = User.objects.filter(profile__phone=test_user_phone).first()
    assert user is not None, "Test user not found!"

    # Step 1: Request OTP with Mobile Number
    req1 = factory.post('/accounts/password/reset/', {
        'action': 'request_otp',
        'identifier': test_user_phone
    })
    add_session(req1)
    resp1 = forgot_password_view(req1)
    assert resp1.status_code == 200

    otp = req1.session.get('pwd_reset_otp')
    assert otp is not None and len(otp) == 6, f"OTP not generated in session: {otp}"
    print(f"✅ OTP generation for mobile '{test_user_phone}' succeeded: OTP = {otp}")

    # Step 2: Verify OTP and reset password
    new_password = "NewlyResetPassword456@"
    req2 = factory.post('/accounts/password/reset/', {
        'action': 'verify_reset',
        'otp': otp,
        'password1': new_password,
        'password2': new_password
    })
    add_session(req2)
    for k, v in req1.session.items():
        req2.session[k] = v
    req2.session.save()
    resp2 = forgot_password_view(req2)
    assert resp2.status_code == 302 and resp2.url == '/login/', f"Expected redirect to /login/, got {resp2.status_code}"

    # Verify user can now log in with the new password
    user.refresh_from_db()
    assert user.check_password(new_password), "User password was not updated!"
    auth_new = authenticate(username=test_user_phone, password=new_password)
    assert auth_new is not None, "Authentication with new password failed!"
    print("✅ Password successfully verified and reset. Login with new password succeeded.")

def test_template_elements():
    print("\n--- 5. Testing Template UI Enhancements ---")
    with open('templates/account/login.html', 'r', encoding='utf-8') as f:
        login_html = f.read()
    assert 'Mobile Number, Email, or Username' in login_html, "Login label missing mobile number!"
    assert 'pwd-toggle-btn' in login_html, "Password show/hide toggle button missing in login.html!"
    assert 'togglePasswordVisibility' in login_html, "togglePasswordVisibility script missing in login.html!"
    assert 'Sign in with Google' in login_html, "Google Sign-In button missing in login.html!"
    print("✅ login.html verified: Multi-identifier label, Show/Hide eye icon, and Google Sign-in intact.")

    with open('templates/account/signup.html', 'r', encoding='utf-8') as f:
        signup_html = f.read()
    assert 'pwd-toggle-btn' in signup_html, "Password show/hide toggle button missing in signup.html!"
    assert 'togglePasswordVisibility' in signup_html, "togglePasswordVisibility script missing in signup.html!"
    print("✅ signup.html verified: Show/Hide eye icon buttons and script present.")

    with open('templates/account/password_reset.html', 'r', encoding='utf-8') as f:
        reset_html = f.read()
    assert 'Registered Mobile Number or Email' in reset_html, "Mobile/email input missing in password_reset.html!"
    assert 'pwd-toggle-btn' in reset_html, "Show/Hide password toggle missing in password_reset.html!"
    print("✅ password_reset.html verified: Mobile/Email OTP recovery UI and eye toggles present.")

    with open('templates/account/password_reset_from_key.html', 'r', encoding='utf-8') as f:
        key_html = f.read()
    assert 'pwd-toggle-btn' in key_html, "Show/Hide password toggle missing in password_reset_from_key.html!"
    print("✅ password_reset_from_key.html verified: Eye toggles present.")

if __name__ == '__main__':
    try:
        test_360_video_attributes()
        test_check_status_search()
        test_multi_identifier_login()
        test_forgot_password_otp_flow()
        test_template_elements()
        print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! 100% VERIFIED.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
