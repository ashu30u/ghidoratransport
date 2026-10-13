import requests
import json

query = """
[out:json][timeout:45];
(
  node["place"~"village|hamlet|town|suburb"](20.4,81.1,21.5,82.2);
);
out body;
"""

endpoints = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass-api.de/api/interpreter"
]
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json"
}

data = None
for url in endpoints:
    try:
        print("Trying endpoint:", url)
        r = requests.post(url, data={"data": query}, headers=headers, timeout=25)
        print("Status:", r.status_code)
        if r.status_code == 200:
            data = r.json()
            break
        else:
            print("Error response:", r.text[:200])
    except Exception as err:
        print("Endpoint error:", err)

if data and "elements" in data:
    elements = data.get("elements", [])
    print(f"Total elements fetched: {len(elements)}")
    villages = {}
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name:en") or tags.get("name")
        name_hi = tags.get("name:hi")
        lat = el.get("lat")
        lon = el.get("lon")
        if name and lat and lon:
            clean_name = name.strip()
            villages[clean_name] = {
                "lat": round(lat, 4),
                "lon": round(lon, 4),
                "hindi": name_hi or ""
            }
    print(f"Unique named villages: {len(villages)}")
    with open("scratch/osm_central_cg_villages.json", "w", encoding="utf-8") as f:
        json.dump(villages, f, indent=2, ensure_ascii=False)
    print("Saved to scratch/osm_central_cg_villages.json")
    for k in villages:
        if any(x in k.lower() for x in ["bire", "sirri", "darba", "kotgaon", "dhetha", "kodebod"]):
            print("Found match:", k, villages[k])
