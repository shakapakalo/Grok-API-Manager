"""Test POST /v1/chat/completions (streaming)"""
import urllib.request, json, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from config import BASE_URL, HEADERS

url  = f"{BASE_URL}/v1/chat/completions"
body = json.dumps({
    "model": "grok-3-mini",
    "stream": True,
    "messages": [{"role": "user", "content": "Count 1 to 5."}]
}).encode()
req = urllib.request.Request(url, data=body, headers=HEADERS, method="POST")

try:
    chunks = []
    with urllib.request.urlopen(req, timeout=60) as r:
        for raw in r:
            line = raw.decode().strip()
            if line.startswith("data: ") and line != "data: [DONE]":
                try:
                    chunk = json.loads(line[6:])
                    delta = chunk["choices"][0]["delta"].get("content","")
                    if delta:
                        chunks.append(delta)
                        print(delta, end="", flush=True)
                except Exception:
                    pass
    print()
    print(f"✅ Stream done — {len(chunks)} chunks received")
except urllib.error.HTTPError as e:
    print("❌ HTTP Error:", e.code, e.read().decode()[:300])
except Exception as e:
    print("❌ Error:", e)
