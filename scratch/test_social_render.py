import os
import sys

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghidora_transport.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from social.models import Profile

client = Client()
user = User.objects.filter(username='ghidora').first()
if not user:
    user = User.objects.create_user(username='ghidora', password='password123')
    Profile.objects.get_or_create(user=user)

client.force_login(user)

print("--- Testing /social/profile/ghidora/ ---")
resp_profile = client.get(f'/social/profile/{user.username}/')
print(f"Profile Status Code: {resp_profile.status_code}")
html_prof = resp_profile.content.decode('utf-8')

has_sidebar = '<aside class="ig-sidebar">' in html_prof
has_topbar = '<header class="gs-social-topbar">' in html_prof
has_old_nav = 'GHIDORA<small>TRANSPORT NETWORK</small>' in html_prof
has_old_footer = 'SYSTEM STATUS: ONLINE' in html_prof
has_studio = 'id="createPostModal"' in html_prof
has_quick_edit = 'id="quickEditProfileModal"' in html_prof
has_crop_canvas = 'id="studioCropCanvas"' in html_prof
has_filter_canvas = 'id="studioFilterCanvas"' in html_prof
has_hamburger = 'ti-menu-2' in html_prof

print(f"Has Left Instagram Sidebar: {has_sidebar}")
print(f"Has Bespoke Social Topbar: {has_topbar}")
print(f"Old Transport Nav Excluded: {not has_old_nav}")
print(f"Old Transport Footer Excluded: {not has_old_footer}")
print(f"Has Post Creative Studio: {has_studio}")
print(f"Has Crop Canvas in Studio: {has_crop_canvas}")
print(f"Has Color Filter Canvas in Studio: {has_filter_canvas}")
print(f"Has Quick Edit Profile Modal: {has_quick_edit}")
print(f"Has Sidebar Hamburger Menu (More): {has_hamburger}")

print("\n--- Testing /social/ (Feed) ---")
resp_feed = client.get('/social/')
print(f"Feed Status Code: {resp_feed.status_code}")
html_feed = resp_feed.content.decode('utf-8')

feed_sidebar = '<aside class="ig-sidebar">' in html_feed
feed_topbar = '<header class="gs-social-topbar">' in html_feed
feed_old_nav = 'GHIDORA<small>TRANSPORT NETWORK</small>' in html_feed
feed_old_footer = 'SYSTEM STATUS: ONLINE' in html_feed

print(f"Feed Has Sidebar: {feed_sidebar}")
print(f"Feed Has Topbar: {feed_topbar}")
print(f"Feed Old Transport Nav Excluded: {not feed_old_nav}")
print(f"Feed Old Footer Excluded: {not feed_old_footer}")

print("\n--- Testing Transport Page (/) ---")
resp_home = client.get('/')
print(f"Home Status Code: {resp_home.status_code}")

print("\n--- Testing All Other Social Pages ---")
pages_to_test = [
    ('/social/explore/', 'Explore'),
    ('/social/reels/', 'Reels'),
    ('/social/inbox/', 'Inbox'),
    ('/social/saved/', 'Saved Posts'),
    ('/social/profile/edit/', 'Edit Profile & Handle'),
]

for url, name in pages_to_test:
    resp = client.get(url)
    assert resp.status_code == 200, f"{name} ({url}) returned {resp.status_code}"
    html = resp.content.decode('utf-8')
    assert '<aside class="ig-sidebar">' in html, f"{name} missing sidebar"
    assert '<header class="gs-social-topbar">' in html, f"{name} missing topbar"
    assert 'GHIDORA<small>TRANSPORT NETWORK</small>' not in html, f"{name} should not have old nav"
    print(f"[OK] {name} ({url}) -> Status 200, Clean Social Layout")

all_ok = all([
    has_sidebar, has_topbar, not has_old_nav, not has_old_footer,
    has_studio, has_crop_canvas, has_filter_canvas, has_quick_edit,
    has_hamburger, feed_sidebar, feed_topbar, not feed_old_nav, not feed_old_footer
])

if all_ok:
    print("\n>>> ALL CHECKS PASSED 100% PERFECTLY! <<<")
else:
    print("\n>>> SOME CHECKS FAILED! <<<")
