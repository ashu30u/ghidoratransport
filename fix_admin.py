path = "pickupwala/admin.py"
try:
    content = open(path, encoding="utf-8").read()
    old = 'list_display = ("order", "text", "is_active")\n    list_editable'
    new = 'list_display = ("order", "text", "is_active")\n    list_display_links = ("text",)\n    list_editable'
    if old in content:
        content = content.replace(old, new)
        open(path, "w", encoding="utf-8").write(content)
        print("FIXED")
    else:
        print("PATTERN NOT FOUND OR ALREADY FIXED")
except Exception as e:
    print("Notice in fix_admin:", e)
