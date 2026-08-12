import os
import sys
import django

sys.path.append(r'C:\Users\dmtam\OneDrive\Desktop\GhidoraTransportProject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghidora_transport.settings')
django.setup()

from occasions.models import Occasion
from occasions.services import dispatch_occasion_notifications

occ = Occasion.objects.filter(name__icontains='hareli').first()
if not occ:
    print("Hareli occasion not found in DB!")
else:
    print(f"Found Occasion: {occ.name}")
    res = dispatch_occasion_notifications(occ, force=True)
    print("Dispatch Result:", res)
