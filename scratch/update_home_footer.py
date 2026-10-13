with open('booking/templates/booking/home.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = None
end_idx = None
for idx, l in enumerate(lines):
    if 'GHIDORA TRANSPORT FOOTER' in l and start_idx is None:
        start_idx = idx - 1  # include the comment header before it
    if '</footer>' in l and start_idx is not None:
        end_idx = idx + 1
        break

if start_idx is not None and end_idx is not None:
    print(f"Replacing lines {start_idx} to {end_idx}")
    new_lines = lines[:start_idx] + ['  {% include "booking/footer.html" %}\n'] + lines[end_idx:]
    with open('booking/templates/booking/home.html', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Done! New total lines:", len(new_lines))
else:
    print("Could not find footer boundaries")
