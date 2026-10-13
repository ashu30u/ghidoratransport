import os, sys, django, re
from pathlib import Path
sys.path.insert(0, str(Path('.')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghidora_transport.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

u = User.objects.filter(username='ghidora').first()
c = Client()
c.force_login(u)
res = c.get('/social/profile/ghidora/')
content = res.content.decode('utf-8')
print('Status:', res.status_code)

scripts = re.findall(r'src=["\'](/static/[^"\']+)["\']', content)
links = re.findall(r'href=["\'](/static/[^"\']+)["\']', content)
print('Static Scripts found:', scripts)
print('Static Links found:', links)

for s in scripts:
    clean = s.split('?')[0].replace('/static/', '')
    p1 = os.path.join('social', 'static', clean)
    p2 = os.path.join('booking', 'static', clean)
    print(f"Script: {s} -> exists: {os.path.exists(p1) or os.path.exists(p2)}")

for l in links:
    clean = l.split('?')[0].replace('/static/', '')
    p1 = os.path.join('social', 'static', clean)
    p2 = os.path.join('booking', 'static', clean)
    print(f"Link: {l} -> exists: {os.path.exists(p1) or os.path.exists(p2)}")
