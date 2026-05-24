"""Test POST /v1/chat/completions (non-streaming)"""
import urllib.request, json, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from config import BASE_URL, HEADERS

url  = f"{BASE_URL}/v1/chat/completions"
body = json.dumps({
    "model": "grok-3-mini",
    "stream": False,
    "messages": [{"role": "user", "content": "Say hello in one sentence."}]
}).encode()
req = urllib.request.Request(url, data=body, headers=HEADERS, method="POST")

try:
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read())
    reply = data["choices"][0]["message"]["content"]
    print("✅ Chat response:", reply[:200])
except urllib.error.HTTPError as e:
    print("❌ HTTP Error:", e.code, e.read().decode()[:300])
except Exception as e:
    print("❌ Error:", e)
