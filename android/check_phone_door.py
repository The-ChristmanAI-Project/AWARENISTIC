"""
check_phone_door.py — AWARENISTIC, Android side
Runs the phone's door against her real mind with a real script. No stand-ins.
Run from the repo root: PYTHONPATH=.:android/app/src/main/python python android/check_phone_door.py
"""
import json
import logging
import sys
import tempfile
from pathlib import Path

logging.disable(logging.CRITICAL)
import phone_door  # noqa: E402

ledger = str(Path(tempfile.mkdtemp()) / "ledger.jsonl")
steps = [
    ("James · WhatsApp", "hi beautiful, I am a sergeant deployed overseas", "flag"),
    ("James · WhatsApp", "we cant video for security reasons, keep this between us", "case"),
    ("Misty · WhatsApp", "dinner at 6?", "clear"),
]
failed = 0
for who, text, want in steps:
    got = json.loads(phone_door.read(text, who, ledger))
    ok = got["level"] == want and bool(got["card_text"])
    failed += not ok
    print(("PASS" if ok else "FAIL"), who, "|", text, "->", got["level"])
print("phone door:", "all passed" if not failed else f"{failed} failed")
sys.exit(1 if failed else 0)
