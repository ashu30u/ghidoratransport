import glob
import os

templates_dir = r"C:\Users\dmtam\OneDrive\Desktop\GhidoraTransportProject\booking\templates\booking"
for filepath in glob.glob(os.path.join(templates_dir, "*.html")):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        if 'mobile-nav-drawer' in content or 'toggleMobileMenu' in content or 'hamburger' in content:
            print(f"=== {os.path.basename(filepath)} ===")
            for i, line in enumerate(content.splitlines()):
                if any(k in line for k in ['mobile-nav-drawer', 'toggleMobileMenu', 'hamburger', 'drawer']):
                    print(f"  Line {i+1}: {line.strip()[:100]}")
