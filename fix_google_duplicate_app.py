import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghidora_transport.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


def fix_duplicate_google_apps():
    site, _ = Site.objects.get_or_create(id=1, defaults={'domain': '127.0.0.1:8000', 'name': 'Ghidora Transport'})
    site.domain = '127.0.0.1:8000'
    site.name = 'Ghidora Transport'
    site.save()

    # Delete ALL existing SocialApp records to ensure zero duplicates
    all_apps = list(SocialApp.objects.all())
    print(f"Total SocialApp entries in database before cleanup: {len(all_apps)}")

    for app in all_apps:
        print(f"Deleting SocialApp ID: {app.id}, name: '{app.name}', provider: '{app.provider}'")
        app.delete()

    client_id = '520482080238-ejsi630q0nv6na0de3if97ug73f5rmmt.apps.googleusercontent.com'

    main_app = SocialApp.objects.create(
        provider='google',
        name='Google Login',
        client_id=client_id,
        secret='',
    )
    main_app.sites.add(site)
    main_app.save()

    print(f"SUCCESS: Recreated single clean Google SocialApp! Active App ID: {main_app.id}, Client ID: {main_app.client_id}")


if __name__ == '__main__':
    fix_duplicate_google_apps()
