import requests
import json
import math

def test_overpass(lat, lon):
    query = f"""
    [out:json][timeout:5];
    (
      node(around:2500,{lat},{lon})["place"~"village|hamlet|suburb|neighbourhood|locality|town"];
      node(around:2500,{lat},{lon})["amenity"];
      way(around:1000,{lat},{lon})["highway"]["name"];
    );
    out tags center 15;
    """
    try:
        r = requests.get("https://overpass-api.de/api/interpreter", params={"data": query}, timeout=6)
        if r.status_code == 200:
            elements = r.json().get("elements", [])
            print(f"Found {len(elements)} elements for ({lat}, {lon})")
            for el in elements:
                t = el.get("tags", {})
                e_lat = el.get("lat") or el.get("center", {}).get("lat")
                e_lon = el.get("lon") or el.get("center", {}).get("lon")
                dist = 0
                if e_lat and e_lon:
                    # rough distance in meters
                    dist = int(math.hypot((e_lat - lat) * 111000, (e_lon - lon) * 105000))
                print(f"  {t.get('name')} | place={t.get('place')} | amenity={t.get('amenity')} | highway={t.get('highway')} | dist={dist}m")
    except Exception as ex:
        print("Overpass error:", ex)

print("--- Testing Nimora (21.164, 81.748) ---")
test_overpass(21.164, 81.748)

print("\n--- Testing Sector 23 (21.1607, 81.7655) ---")
test_overpass(21.1607, 81.7655)

print("\n--- Testing Kodebod (20.932, 81.654) ---")
test_overpass(20.932, 81.654)
