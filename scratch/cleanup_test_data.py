import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghidora_transport.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
from social.models import Post, Follow, SavedPost, Notification, Report, Comment, CommentLike

User = get_user_model()

test_users = User.objects.filter(username__in=['test_driver_alpha', 'test_client_beta'])
for u in test_users:
    Notification.objects.filter(recipient=u).delete()
    Notification.objects.filter(sender=u).delete()
    Follow.objects.filter(follower=u).delete()
    Follow.objects.filter(following=u).delete()
    SavedPost.objects.filter(user=u).delete()
    Report.objects.filter(reporter=u).delete()
    Post.objects.filter(author=u).delete()
    u.delete()

print("Cleaned up test data successfully.")
