path = "pickupwala/admin.py"
content = open(path, encoding="utf-8").read()

old = 'list_display = ("order", "text", "is_active")
    list_editable'
new = 'list_display = ("order", "text", "is_active")
    list_display_links = ("text",)
    list_editable'

if old in content:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("FIXED")
else:
    print("PATTERN NOT FOUND")

print("---CURRENT CONTENT---")
print(open(path, encoding="utf-8").read())
