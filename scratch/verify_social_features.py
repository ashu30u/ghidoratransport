import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghidora_transport.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from social.models import Post, Comment, CommentLike, Follow, SavedPost, Notification, Report, Story, StoryReaction

User = get_user_model()

def run_tests():
    print("--- STARTING GHIDORA SOCIAL VERIFICATION ---")
    
    # 1. Setup Test Users
    u1, _ = User.objects.get_or_create(username='test_driver_alpha', defaults={'email': 'alpha@ghidora.in'})
    u1.set_password('pass1234')
    u1.save()
    if hasattr(u1, 'profile'):
        u1.profile.is_driver = True
        u1.profile.save()

    u2, _ = User.objects.get_or_create(username='test_client_beta', defaults={'email': 'beta@ghidora.in'})
    u2.set_password('pass1234')
    u2.save()

    c1 = Client()
    c1.force_login(u1)

    c2 = Client()
    c2.force_login(u2)

    # 2. Test Follow / Unfollow Flow
    Follow.objects.filter(follower__in=[u1, u2]).delete()
    print("\n[TEST 1] Testing Follow Toggle...")
    res = c1.post(f'/social/user/{u2.username}/follow/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert res.status_code == 200, f"Follow failed: {res.status_code}"
    data = res.json()
    assert data['ok'] is True and data['following'] is True, f"Unexpected response: {data}"
    assert Follow.objects.filter(follower=u1, following=u2).exists(), "Follow record not found in DB!"
    print("[PASS] Follow toggle (Follow) passed!")

    # Check notification for follow
    notif = Notification.objects.filter(recipient=u2, sender=u1, notification_type='FOLLOW').first()
    assert notif is not None, "Follow notification was not created!"
    print("[PASS] Follow notification created!")

    # Test Followers List API
    res = c2.get(f'/social/api/followers/{u2.username}/')
    assert res.status_code == 200
    followers_data = res.json()
    assert followers_data['ok'] is True
    assert any(f['username'] == u1.username for f in followers_data['followers'])
    print("[PASS] Followers API returned follower u1!")

    # 3. Test Post Creation with Location
    print("\n[TEST 2] Testing Post with Location...")
    post = Post.objects.create(author=u1, content="Heavy cargo dispatched to #Jaipur via #NH48! @test_client_beta take note.", location="Gurugram Hub 01")
    assert post.location == "Gurugram Hub 01"
    print(f"[PASS] Post created with ID {post.id} and location '{post.location}'")

    # 4. Test Like Post
    print("\n[TEST 3] Testing Like Post...")
    res = c2.post(f'/social/post/{post.id}/like/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert res.status_code == 200
    like_data = res.json()
    assert like_data['liked'] is True
    post.refresh_from_db()
    assert post.like_count == 1
    # Check like notification
    notif_like = Notification.objects.filter(recipient=u1, sender=u2, notification_type='LIKE', post=post).first()
    assert notif_like is not None, "Post like notification not created!"
    print("[PASS] Post liked, count incremented to 1, notification created!")

    # 5. Test Bookmark / Save Post
    print("\n[TEST 4] Testing Save Post...")
    res = c2.post(f'/social/post/{post.id}/save/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert res.status_code == 200
    save_data = res.json()
    assert save_data['ok'] is True and save_data['saved'] is True
    assert SavedPost.objects.filter(user=u2, post=post).exists()
    
    # Check saved_posts view
    res = c2.get('/social/saved/')
    assert res.status_code == 200
    assert 'Saved Posts' in res.content.decode()
    print("[PASS] Post saved and rendered in /social/saved/!")

    # 6. Test Comments and Replies
    print("\n[TEST 5] Testing Comments and Replies...")
    res = c2.post(f'/social/post/{post.id}/comment/', {'content': 'Driver assigned on time, great!'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert res.status_code == 200
    comm_data = res.json()
    assert comm_data['ok'] is True
    comment_id = comm_data['comment']['id']
    comment_obj = Comment.objects.get(id=comment_id)
    assert comment_obj.parent is None

    # Reply to comment
    res = c1.post(f'/social/post/{post.id}/comment/', {'content': 'Roger that, safe transit guaranteed.', 'parent_id': comment_id}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert res.status_code == 200
    reply_data = res.json()
    assert reply_data['ok'] is True
    reply_id = reply_data['comment']['id']
    reply_obj = Comment.objects.get(id=reply_id)
    assert reply_obj.parent == comment_obj
    print("[PASS] Parent comment and nested reply created successfully!")

    # 7. Test Comment Like
    print("\n[TEST 6] Testing Comment Like...")
    res = c1.post(f'/social/comment/{comment_id}/like/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert res.status_code == 200
    clike_data = res.json()
    assert clike_data['ok'] is True and clike_data['liked'] is True
    assert CommentLike.objects.filter(user=u1, comment=comment_obj).exists()
    print("[PASS] Comment like registered!")

    # 8. Test Notifications API & Read Mark
    print("\n[TEST 7] Testing Notifications List and Mark Read...")
    res = c1.get('/social/api/notifications/')
    assert res.status_code == 200
    n_data = res.json()
    assert n_data['ok'] is True
    assert n_data['unread_count'] > 0
    print(f"[PASS] Notifications retrieved. Unread count: {n_data['unread_count']}")

    res = c1.post('/social/api/notifications/read/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert res.status_code == 200
    assert res.json()['ok'] is True
    assert Notification.objects.filter(recipient=u1, is_read=False).count() == 0
    print("[PASS] All notifications marked as read!")

    # 9. Test Live Debounced Search API
    print("\n[TEST 8] Testing Search API...")
    res = c1.get('/social/api/search/?q=alpha')
    assert res.status_code == 200
    s_data = res.json()
    assert s_data['ok'] is True
    assert any(u['username'] == 'test_driver_alpha' for u in s_data['users'])

    res = c1.get('/social/api/search/?q=jaipur')
    assert res.status_code == 200
    s_tag_data = res.json()
    assert any('jaipur' in h['tag'].lower() for h in s_tag_data['hashtags'])
    print("[PASS] Search API found users and hashtags successfully!")

    # 10. Test Share Post via Direct Message
    print("\n[TEST 9] Testing Share Post via DM...")
    res = c1.post('/social/api/share/dm/', {'recipient_username': u2.username, 'post_id': post.id}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert res.status_code == 200
    assert res.json()['ok'] is True
    print("[PASS] Post shared directly into private DM conversation!")

    # 11. Test Report Moderation API
    print("\n[TEST 10] Testing Moderation Report API...")
    res = c2.post('/social/api/report/', {'target_type': 'post', 'target_id': post.id, 'reason': 'spam', 'details': 'Test moderation flag'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert res.status_code == 200
    assert res.json()['ok'] is True
    assert Report.objects.filter(reporter=u2, target_type='POST', target_id=post.id).exists()
    print("[PASS] Content report successfully logged in database!")

    # 12. Test Profile View Data
    print("\n[TEST 11] Testing Profile Rendering...")
    res = c1.get(f'/social/profile/{u2.username}/')
    assert res.status_code == 200
    content = res.content.decode()
    assert "325 followers" not in content, "Found hardcoded 325 followers in profile!"
    assert "308 following" not in content, "Found hardcoded 308 following in profile!"
    assert "alert('Followed" not in content, "Found fake follow alert in profile!"
    print("[PASS] Verified profile has NO fake alerts and NO hardcoded 325/308 counts!")

    print("\n==========================================")
    print("ALL GHIDORA SOCIAL FUNCTIONALITY VERIFIED!")
    print("==========================================")

if __name__ == '__main__':
    run_tests()
