with open('booking/templates/booking/home.html', 'r', encoding='utf-8', errors='ignore') as fp:
    lines = fp.readlines()

for i, l in enumerate(lines):
    if 'form-row' in l and ('{' in l or ':' in l or '<style' in l):
        print(f"Line {i+1}: {l.strip()[:80]}")
