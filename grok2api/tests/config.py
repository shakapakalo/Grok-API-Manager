import os

BASE_URL   = os.getenv("GROK2API_URL",   "http://217.77.8.115:8885")
API_KEY    = os.getenv("GROK2API_KEY",   "ranaji")
ADMIN_PASS = os.getenv("GROK2API_ADMIN", "grok2api")
SSO_TOKEN  = os.getenv("GROK2API_TOKEN", "")

if not SSO_TOKEN:
    raise SystemExit(
        "ERROR: GROK2API_TOKEN env var set karo pehle.\n"
        "  export GROK2API_TOKEN='your_sso_token_here'\n"
        "  python3 00_add_account.py"
    )

HEADERS   = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
ADMIN_HDR = {"Authorization": f"Bearer {ADMIN_PASS}", "Content-Type": "application/json"}
