"""Test POST /v1/images/edits — uses a small test PNG."""
import urllib.request, urllib.parse, sys, json, os, base64, struct, zlib
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from config import BASE_URL, API_KEY

def _make_png(w=64, h=64):
    """Create a minimal solid-blue PNG in memory."""
    def chunk(name, data):
        c = zlib.crc32(name + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", c)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    raw  = b"".join(b"\x00" + b"\x00\x60\xFF" * w for _ in range(h))
    idat = zlib.compress(raw)

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", idat)
        + chunk(b"IEND", b"")
    )
    return png

png_bytes = _make_png()

boundary = "----TestBoundary7777"
body_parts = []
body_parts.append(
    f'--{boundary}\r\nContent-Disposition: form-data; name="model"\r\n\r\ngrok-imagine-image-edit'.encode()
)
body_parts.append(
    f'--{boundary}\r\nContent-Disposition: form-data; name="prompt"\r\n\r\nAdd a bright yellow sun in the top right corner'.encode()
)
body_parts.append(
    f'--{boundary}\r\nContent-Disposition: form-data; name="image[]"; filename="test.png"\r\nContent-Type: image/png\r\n\r\n'.encode()
    + png_bytes
)
body_parts.append(
    f'--{boundary}\r\nContent-Disposition: form-data; name="n"\r\n\r\n1'.encode()
)
body_parts.append(
    f'--{boundary}\r\nContent-Disposition: form-data; name="response_format"\r\n\r\nurl'.encode()
)
body = b"\r\n".join(body_parts) + f"\r\n--{boundary}--\r\n".encode()

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": f"multipart/form-data; boundary={boundary}",
    "Content-Length": str(len(body)),
}
req = urllib.request.Request(f"{BASE_URL}/v1/images/edits", data=body, headers=headers, method="POST")

try:
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.loads(r.read())
    url_result = data["data"][0].get("url","")
    print("✅ Image edit done!")
    print("   URL:", url_result[:120])
except urllib.error.HTTPError as e:
    err = e.read().decode()
    try:
        print("❌ API Error:", json.loads(err).get("error",{}).get("message", err)[:300])
    except Exception:
        print("❌ HTTP Error:", e.code, err[:300])
except Exception as e:
    print("❌ Error:", e)
