import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ghidora_transport.settings")
import django
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from social.models import Profile, Post
from social.forms import ProfileForm
from social.views import edit_profile

def test_all():
    print("--- 1. Testing ProfileForm Name & Username Customization ---")
    User.objects.filter(username__in=["testuser_studio_1", "custom_handle_99", "ajax_user_handle", "existing_user_abc"]).delete()
    u1 = User.objects.create(username="testuser_studio_1", first_name="Studio Tester")
    p1, _ = Profile.objects.get_or_create(user=u1)
    
    # Form initialization
    form = ProfileForm(instance=p1)
    assert form.fields["username"].initial == "testuser_studio_1"
    assert form.fields["first_name"].initial == "Studio Tester"
    print("[PASS] ProfileForm initialized with username and first_name.")

    # Valid name & username update
    form_valid = ProfileForm(
        data={"first_name": "New Display Name", "username": "custom_handle_99", "gender": "Prefer not to say"},
        instance=p1
    )
    assert form_valid.is_valid(), f"Errors: {form_valid.errors}"
    form_valid.save()
    u1.refresh_from_db()
    assert u1.first_name == "New Display Name"
    assert u1.username == "custom_handle_99"
    print(f"[PASS] User updated to name='{u1.first_name}', username='{u1.username}'.")

    # Duplicate username rejection test
    u2, _ = User.objects.get_or_create(username="existing_user_abc")
    p2, _ = Profile.objects.get_or_create(user=u2)
    form_dup = ProfileForm(
        data={"first_name": "Another", "username": "custom_handle_99", "gender": "Prefer not to say"},
        instance=p2
    )
    assert not form_dup.is_valid(), "Duplicate username should have been rejected!"
    assert "username" in form_dup.errors
    print(f"[PASS] Duplicate username rejected as expected: {form_dup.errors['username']}")

    # Invalid characters in username test
    form_invalid = ProfileForm(
        data={"first_name": "Test", "username": "bad user@name!", "gender": "Prefer not to say"},
        instance=p1
    )
    assert not form_invalid.is_valid()
    assert "username" in form_invalid.errors
    print(f"[PASS] Invalid username characters rejected: {form_invalid.errors['username']}")

    print("\n--- 2. Testing AJAX edit_profile View ---")
    client = Client()
    client.force_login(u1)
    resp = client.post(
        "/social/profile/edit/",
        data={"first_name": "AJAX Name", "username": "ajax_user_handle", "gender": "Male", "ajax": "1"},
        headers={"x-requested-with": "XMLHttpRequest"}
    )
    assert resp.status_code == 200, f"Status: {resp.status_code}, Content: {resp.content}"
    import json
    data = json.loads(resp.content)
    assert data["ok"] is True
    assert data["username"] == "ajax_user_handle"
    print(f"[PASS] AJAX edit_profile returned JSON ok: {data['message']}")

    print("\n--- 3. Testing Client Rendering of Social Navbar vs Transport Navbar ---")
    u1.refresh_from_db()
    client = Client()
    client.force_login(u1)

    # Social Profile Page
    resp_social = client.get(f"/social/profile/{u1.username}/")
    assert resp_social.status_code == 200
    content_social = resp_social.content.decode("utf-8")
    
    # Must have dedicated social navbar
    assert "gs-navbar" in content_social, "Social navbar missing from profile!"
    assert "gs-social-tag" in content_social, "Social tag badge missing!"
    assert "Search Ghidora..." in content_social, "Social search pill missing!"
    assert "quickEditProfileModal" in content_social, "Quick Edit Profile modal missing from profile!"
    print("[PASS] Social Profile page renders dedicated gs-navbar and quick edit modal.")

    # Social Feed Page
    resp_feed = client.get("/social/")
    assert resp_feed.status_code == 200
    content_feed = resp_feed.content.decode("utf-8")
    assert "gs-navbar" in content_feed, "Social navbar missing from feed!"
    assert "studioCropCanvas" in content_feed, "Studio crop canvas missing from feed!"
    assert "studioFilterCanvas" in content_feed, "Studio filter canvas missing from feed!"
    assert "applyStudioFilter" in content_feed, "Filter presets missing from feed!"
    print("[PASS] Social Feed renders dedicated gs-navbar and Post Creative Studio.")

    # Social Explore Page
    resp_explore = client.get("/social/explore/")
    assert resp_explore.status_code == 200
    content_explore = resp_explore.content.decode("utf-8")
    assert "gs-navbar" in content_explore, "Social navbar missing from explore!"

    # Social Saved Page
    resp_saved = client.get("/social/saved/")
    assert resp_saved.status_code == 200
    content_saved = resp_saved.content.decode("utf-8")
    assert "gs-navbar" in content_saved, "Social navbar missing from saved!"

    # Transport / Home Page (Ensure it doesn't leak gs-navbar)
    resp_home = client.get("/")
    assert resp_home.status_code == 200
    content_home = resp_home.content.decode("utf-8")
    assert "gs-navbar" not in content_home, "Social navbar should not leak onto transport homepage!"
    print("[PASS] Transport homepage does not contain gs-navbar.")

    # Cleanup test users
    u1.delete()
    u2.delete()
    print("\n[ALL TESTS PASSED SUCCESSFULLY!]")

if __name__ == "__main__":
    test_all()
