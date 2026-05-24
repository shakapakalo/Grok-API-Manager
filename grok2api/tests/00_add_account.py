"""Add super account to grok2api."""
import urllib.request, json, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from config import BASE_URL, ADMIN_HDR, SSO_TOKEN

url  = f"{BASE_URL}/admin/api/tokens/add"
body = json.dumps({"tokens": [SSO_TOKEN], "pool": "super"}).encode()
req  = urllib.request.Request(url, data=body, headers=ADMIN_HDR, method="POST")

try:
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    print("✅ Account added:", data)
except urllib.error.HTTPError as e:
    print("❌ HTTP Error:", e.code, e.read().decode())
except Exception as e:
    print("❌ Error:", e)
