import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghidora_transport.settings')
django.setup()

from allauth.socialaccount.models import SocialApp

print("--- Deleting database SocialApp records so settings.py APP configuration takes effect ---")
deleted_count, _ = SocialApp.objects.filter(provider='google').delete()
print(f"Deleted {deleted_count} database SocialApp records for google.")

print("All database duplicates cleared! allauth will now use settings.py configuration cleanly.")
