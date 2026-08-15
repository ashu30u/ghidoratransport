import os

req_path = r"C:\Users\dmtam\OneDrive\Desktop\GhidoraTransportProject\requirements.txt"

content = ""
for encoding in ['utf-16le', 'utf-16', 'utf-8', 'cp1252', 'latin-1']:
    try:
        with open(req_path, 'r', encoding=encoding) as f:
            content = f.read()
        if content.strip():
            print(f"Successfully read with encoding: {encoding}")
            break
    except Exception as e:
        continue

# Clean up null bytes if any
content = content.replace('\x00', '').strip()

print("File contents (first 200 chars):")
print(content[:200])

# Write back as pure UTF-8 without BOM
with open(req_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print("Saved requirements.txt as clean UTF-8!")
