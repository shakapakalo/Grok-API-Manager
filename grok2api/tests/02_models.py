"""Test GET /v1/models"""
import urllib.request, json, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from config import BASE_URL, HEADERS

url = f"{BASE_URL}/v1/models"
req = urllib.request.Request(url, headers={k:v for k,v in HEADERS.items() if k!="Content-Type"})

try:
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    models = data.get("data", [])
    print(f"✅ Models available: {len(models)}")
    for m in models[:10]:
        print(f"   {m.get('id','?')}")
    if len(models) > 10:
        print(f"   ... aur {len(models)-10} models")
except urllib.error.HTTPError as e:
    print("❌ HTTP Error:", e.code, e.read().decode())
except Exception as e:
    print("❌ Error:", e)
