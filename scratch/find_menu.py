with open('booking/templates/booking/home.html', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    s = l.strip().lower()
    if any(k in s for k in ['<header', 'class="nav', 'class="menu', 'id="menu', 'hamburger', 'mobile-nav', 'side-nav', 'navbar']):
        if not s.startswith('/*') and not s.startswith('*'):
            print(f"{i+1}: {l.strip()[:100]}")
