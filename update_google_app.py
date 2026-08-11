import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghidora_transport.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

def setup_google_app():
    site, _ = Site.objects.get_or_create(id=1, defaults={'domain': '127.0.0.1:8000', 'name': 'Ghidora Transport'})
    site.domain = '127.0.0.1:8000'
    site.name = 'Ghidora Transport'
    site.save()

    client_id = '520482080238-ejsi630q0nv6na0de3if97ug73f5rmmt.apps.googleusercontent.com'
    
    app, created = SocialApp.objects.get_or_create(
        provider='google',
        defaults={
            'name': 'Google Login',
            'client_id': client_id,
            'secret': 'YOUR_CLIENT_SECRET_HERE',
        }
    )
    
    app.client_id = client_id
    app.sites.add(site)
    app.save()
    
    print(f"DEBUG: SocialApp updated successfully. ID: {app.id}, Client ID: {app.client_id}")

if __name__ == '__main__':
    setup_google_app()
