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
trusted = "614 555 0100"
# (who, text, level she should reach, whether her card should be ready for the trusted person)
steps = [
    ("James · WhatsApp", "hi beautiful, I am a sergeant deployed overseas", "flag", True),
    ("James · WhatsApp", "we cant video for security reasons, keep this between us", "case", True),
    ("Misty · WhatsApp", "dinner at 6?", "clear", False),
]
failed = 0
for who, text, want, ready in steps:
    got = json.loads(phone_door.read(text, who, ledger, trusted))
    route = got["trusted"]
    ok = (got["level"] == want and bool(got["card_text"]) and route["ok"] is ready
          and (not ready or (route["kind"] == "text" and route["to"] == "6145550100"
                             and route["body"] == got["card_text"])))
    failed += not ok
    print(("PASS" if ok else "FAIL"), who, "|", text, "->", got["level"],
          "| trusted:", route.get("kind") or route.get("reason"))
print("phone door:", "all passed" if not failed else f"{failed} failed")
sys.exit(1 if failed else 0)
