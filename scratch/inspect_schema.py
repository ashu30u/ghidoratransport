import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghidora_transport.settings')
import django
django.setup()

from django.apps import apps
from django.contrib.auth import get_user_model

models_to_check = [
    ('auth', 'User'),
    ('booking', 'Booking'),
    ('booking', 'BookingAttachment'),
    ('booking', 'Review'),
    ('booking', 'PredefinedRouteFare'),
    ('booking', 'PredefinedRouteDistance'),
    ('drivers', 'Driver'),
    ('drivers', 'Vehicle'),
    ('payments', 'PaymentRequest'),
    ('payments', 'PaymentProof'),
    ('payments', 'Receipt'),
]

for app_label, model_name in models_to_check:
    model = apps.get_model(app_label, model_name)
    print(f"\n================ MODEL: {model.__name__} (Table: {model._meta.db_table}) ================")
    for f in model._meta.fields:
        pk_str = " [PK]" if f.primary_key else ""
        fk_str = f" [FK -> {f.related_model.__name__}]" if f.is_relation and f.related_model else ""
        null_str = " (nullable)" if f.null else ""
        print(f"  - {f.name}: {f.get_internal_type()}{pk_str}{fk_str}{null_str}")
    for rel in model._meta.related_objects:
        print(f"  * Reverse Rel: {rel.get_accessor_name()} <- {rel.related_model.__name__}.{rel.field.name}")

