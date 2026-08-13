# Pickupwala — admin-managed player for Ghidora Transport

Drop the `pickupwala/` folder into your Django project (next to your other apps,
e.g. the booking app / drivers app).

## 1. Install

```bash
pip install Pillow   # needed for the Song cover_image field
```

## 2. settings.py

```python
INSTALLED_APPS = [
    ...,
    "pickupwala",
]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"   # wherever you already serve uploads from
```

## 3. project urls.py

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    ...,
    path("pickupwala/", include("pickupwala.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## 4. Migrate

```bash
python manage.py makemigrations pickupwala
python manage.py migrate
```

## 5. Add songs & shayari

Go to `/admin/` → **Pickupwala Radio** → **Songs** / **Shayaris**.

- **Song**: title, artist, upload the audio file, optional cover image, duration
  (seconds — leave 0 if unsure), trip km (just cosmetic, shown on the road
  progress bar), order, active toggle.
- **Shayari**: the line of text shown on the signage board, order, active toggle.

Anything you add/edit here shows up on the live page immediately — no code
changes, no deploy. Uncheck "is_active" to pull a song or line without
deleting it.

## 6. View the player

`/pickupwala/` — the page fetches `/pickupwala/api/playlist/` on load and
builds the playlist + shayari cycle from whatever is active in the admin.

## Truck image

The player now shows your own image instead of the drawn truck — it's loaded
from `{% static 'images/truck.png' %}` in `templates/pickupwala/player.html`,
which resolves to `booking/static/images/truck.png` in your project (Django's
static finder uses each app's `static/` folder as the root, so no `booking/`
prefix is needed in the path). Either:

- rename your uploaded file to `truck.png`, or
- open `player.html` and change `'images/truck.png'` to your actual filename.

## Admin

Songs and shayaris are managed from the **same** `/admin/` your booking and
drivers apps already use — Pickupwala is just another app in that project, so
there's no separate login or panel to set up.

## Notes

- Horn 🎺 and radio-tune 📻 click sounds are static files under
  `static/pickupwala/audio/` (placeholder synthesized sounds) — swap them for
  real recordings any time, they aren't admin-managed since you only asked
  for songs + shayari to be editable.
- The whole player bar (`.player-inner`, controls, signage, playlist sheet) is
  built with `backdrop-filter: blur() saturate()` + translucent borders/shadows
  in `static/pickupwala/css/player.css` — true glassmorphism, so the sunset
  scenery stays visible through it. Tweak `--glass-bg` / `--glass-border` /
  `--glass-shadow` in `:root` to adjust the effect.
