import requests
import json

villages = [
    'Birejhar', 'Sirri', 'Darba', 'Kotgaon', 'Kulhadi', 'Dhetha', 'Fusera', 'Hathband', 'Karga', 
    'Jamgaon', 'Nimora', 'Tuta', 'Bendri', 'Bhatgaon', 'Kodebod', 'Hasda', 'Marod', 'Silphati', 
    'Megha', 'Charmudhiya', 'Hanchalpur', 'Durgagahan', 'Sankra', 'Sorid', 'Rudri', 'Gangrel',
    'Dhaneli', 'Mujgahan', 'Datrenga', 'Raweli', 'Julum', 'Seoni', 'Boria Kalan', 'Sejbahar',
    'Mana', 'Dumatara', 'Devpuri', 'Mandir Hasaud', 'Chandkhuri', 'Gobra Nawapara', 'Patan',
    'Selud', 'Utai', 'Gunderdehi', 'Anda', 'Junwani', 'Smriti Nagar', 'Nehru Nagar', 'Supela',
    'Kurud', 'Dhamtari', 'Abhanpur', 'Rajim', 'Arang', 'Tilda', 'Kharora', 'Simga', 'Balod'
]

results_dict = {}
for v in villages:
    try:
        r = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={v}&count=5&format=json", timeout=5)
        if r.status_code == 200:
            res_list = r.json().get('results', [])
            cg = [x for x in res_list if 'chhattisgarh' in str(x.get('admin1', '')).lower()]
            if cg:
                best = cg[0]
                results_dict[v] = {
                    'lat': round(best['latitude'], 4),
                    'lon': round(best['longitude'], 4),
                    'admin2': best.get('admin2', ''),
                    'admin3': best.get('admin3', '')
                }
    except Exception as e:
        print("Err for", v, e)

with open("scratch/cg_villages_dataset.json", "w", encoding="utf-8") as f:
    json.dump(results_dict, f, indent=2)

print(f"Successfully fetched {len(results_dict)} villages!")
