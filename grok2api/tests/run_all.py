"""Run all tests in order and show a summary."""
import subprocess, sys, os

TESTS = [
    ("00 — Add Account",      "00_add_account.py"),
    ("01 — List Accounts",    "01_list_accounts.py"),
    ("02 — GET /v1/models",   "02_models.py"),
    ("03 — Chat (no-stream)", "03_chat.py"),
    ("04 — Chat (stream)",    "04_chat_stream.py"),
    ("05 — Image Generate",   "05_image_generate.py"),
    ("06 — Image Edit",       "06_image_edit.py"),
]

GREEN = "\033[92m"; RED = "\033[91m"; YELLOW = "\033[93m"; RESET = "\033[0m"; BOLD = "\033[1m"
DIR   = os.path.dirname(os.path.abspath(__file__))

results = []
for name, script in TESTS:
    print(f"\n{BOLD}{'='*55}{RESET}")
    print(f"{BOLD}Test: {name}{RESET}")
    print(f"{'='*55}")
    r = subprocess.run([sys.executable, os.path.join(DIR, script)], capture_output=False)
    passed = r.returncode == 0
    results.append((name, passed))

print(f"\n{BOLD}{'='*55}")
print("SUMMARY")
print(f"{'='*55}{RESET}")
for name, passed in results:
    icon = f"{GREEN}✅ PASS{RESET}" if passed else f"{RED}❌ FAIL{RESET}"
    print(f"  {icon}  {name}")

passed_count = sum(1 for _, p in results if p)
print(f"\n{BOLD}Result: {passed_count}/{len(results)} passed{RESET}\n")
