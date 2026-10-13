import os, sys, django
sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghidora_transport.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from booking.views import forgot_password_view

rf = RequestFactory()
req = rf.post('/accounts/password/reset/', {'action': 'request_otp', 'identifier': '6268814185'})
middleware = SessionMiddleware(lambda r: None)
middleware.process_request(req)
req.session.save()

res = forgot_password_view(req)
print('Status code:', res.status_code)
content = res.content.decode('utf-8')
print('Does content contain Verification OTP Code pill?:', 'Verification OTP Code' in content)
print('Does content contain sent_email_hint (d***9@gmail.com)?:', 'd***9@gmail.com' in content)
print('Does input field prefill OTP?:', 'autocomplete="one-time-code"\n            >' in content or 'autocomplete="one-time-code"' in content)
