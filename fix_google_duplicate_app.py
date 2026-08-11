import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghidora_transport.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

def fix_duplicate_google_apps():
    site, _ = Site.objects.get_or_create(id=1, defaults={'domain': '127.0.0.1:8000', 'name': 'Ghidora Transport'})
    
    google_apps = list(SocialApp.objects.filter(provider='google'))
    print(f"Found {len(google_apps)} Google SocialApp entries in database.")
    
    client_id = '520482080238-ejsi630q0nv6na0de3if97ug73f5rmmt.apps.googleusercontent.com'

    if len(google_apps) > 1:
        # Keep the first one, delete all duplicate entries
        main_app = google_apps[0]
        for duplicate in google_apps[1:]:
            print(f"Deleting duplicate SocialApp ID: {duplicate.id}")
            duplicate.delete()
    elif len(google_apps) == 1:
        main_app = google_apps[0]
    else:
        main_app = SocialApp.objects.create(
            provider='google',
            name='Google Login',
            client_id=client_id,
            secret=''
        )
        print(f"Created new SocialApp ID: {main_app.id}")

    main_app.client_id = client_id
    main_app.sites.add(site)
    main_app.save()
    
    print(f"SUCCESS: Fixed Google SocialApp! Active App ID: {main_app.id}, Client ID: {main_app.client_id}")

if __name__ == '__main__':
    fix_duplicate_google_apps()
