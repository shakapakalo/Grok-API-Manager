"""Test POST /v1/images/generations"""
import urllib.request, json, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from config import BASE_URL, HEADERS

url  = f"{BASE_URL}/v1/images/generations"
body = json.dumps({
    "model": "grok-2-image",
    "prompt": "A red apple on a white table, photorealistic",
    "n": 1,
    "response_format": "url"
}).encode()
req = urllib.request.Request(url, data=body, headers=HEADERS, method="POST")

try:
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read())
    url_result = data["data"][0].get("url","")
    print("✅ Image generated!")
    print("   URL:", url_result[:120])
except urllib.error.HTTPError as e:
    print("❌ HTTP Error:", e.code, e.read().decode()[:300])
except Exception as e:
    print("❌ Error:", e)
