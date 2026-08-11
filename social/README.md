# Adding the `social` app to Ghidora Transport

This is a real, working Django app — not a snippet. It gives you:
user profiles (auto-created for every user), a paginated feed, posting
(text + optional photo), likes, and comments. Follow requests, verified
badges, stories, etc. are *not* in here yet — this is step one.

## 1. Copy the folder in

Copy the whole `social/` folder so it sits next to your other apps:

```
GhidoraTransportProject/
├── ghidora_transport/      <- settings app
├── booking/
├── drivers/
├── chatbot/
├── occasions/
└── social/                 <- new, from this package
```

## 2. Install Pillow (needed for image uploads)

In your `.venv` (PowerShell):

```
pip install Pillow
```

## 3. Register the app

In `ghidora_transport/settings.py`, add `"social"` to `INSTALLED_APPS`
(same list where `"booking"`, `"drivers"`, `"chatbot"`, `"occasions"` are).

## 4. Media files (for avatars and post photos)

If you don't already have this in `settings.py`, add:

```python
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

And in your project's main `urls.py` (the one in `ghidora_transport/`),
make sure media is served in development:

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ...your existing routes...
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## 5. Wire up the URLs

In that same project `urls.py`, add:

```python
from django.urls import path, include

urlpatterns = [
    # ...your existing routes...
    path("social/", include("social.urls")),
]
```

## 6. Run migrations

```
python manage.py makemigrations social
python manage.py migrate
```

This creates the `Profile`, `Post`, `Like`, and `Comment` tables, and
from now on every user who registers automatically gets a `Profile`
row (handled by the signal in `social/signals.py` — you don't need to
touch your existing registration view).

## 7. Templates assume a `base.html`

The templates use `{% extends "base.html" %}` with two blocks:
`{% block extra_css %}` and `{% block content %}`. If your existing
`base.html` (used by the booking app) has different block names,
either rename the blocks in these templates to match, or add those
two block names to your `base.html`.

## 8. Add a nav link

Wherever your site navigation lives, add a link to the feed:

```html
<a href="{% url 'social:feed' %}">Feed</a>
```

And on a user's own dashboard/profile widget:

```html
<a href="{% url 'social:profile' request.user.username %}">My profile</a>
```

## 9. Marking a user as a driver

`Profile.is_driver` is a plain boolean, off by default. For now, set it
manually in the Django admin (Social → Profiles) for driver accounts so
the green "DRIVER" badge shows on their posts and profile. Wiring this
up automatically from your `drivers.Driver` model is a natural next
step once you're ready — it's a one-line addition to the `Profile`
model (a FK or a signal tied to driver approval) but I didn't want to
guess how your driver-approval flow works without checking with you
first.

## 10. Try it

```
python manage.py runserver
```

Log in, go to `/social/`, write a post, like it, comment on it, then
visit your own profile page.

---

**What's deliberately not here yet:** follow/unfollow, verified badges
beyond the basic driver flag, nested comment replies, stories, reels,
DMs, and anything AI-related. Once this foundation is solid on your
machine, tell me which of those to build next and I'll build it the
same way — real models, real views, real templates, wired into what
you already have.
