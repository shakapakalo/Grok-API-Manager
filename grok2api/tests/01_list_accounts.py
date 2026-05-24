"""List all accounts in grok2api."""
import urllib.request, json, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from config import BASE_URL, ADMIN_HDR

url = f"{BASE_URL}/admin/api/tokens"
req = urllib.request.Request(url, headers=ADMIN_HDR, method="GET")

try:
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    accounts = data.get("tokens") or data.get("data") or data
    if isinstance(accounts, list):
        print(f"✅ Total accounts: {len(accounts)}")
        for a in accounts:
            tok = a.get("token","")
            print(f"   pool={a.get('pool','?'):8}  disabled={a.get('disabled',False)}  token=...{tok[-20:]}")
    else:
        print("✅ Response:", json.dumps(data, indent=2))
except urllib.error.HTTPError as e:
    print("❌ HTTP Error:", e.code, e.read().decode())
except Exception as e:
    print("❌ Error:", e)
