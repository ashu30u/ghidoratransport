import urllib.request
import json

try:
    with urllib.request.urlopen('http://127.0.0.1:4040/api/tunnels', timeout=3) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        tunnels = data.get('tunnels', [])
        if not tunnels:
            print("No active tunnels found in ngrok.")
        for t in tunnels:
            print("ACTIVE_TUNNEL:", t.get('public_url'))
except Exception as e:
    print("NGROK_NOT_RUNNING:", e)
