"""
phone_door.py — AWARENISTIC, Android side
The one door between the phone and her mind. The phone hands her a message and who
sent it; she reads it against the whole thread with that stranger, on the phone, and
returns her card. Her mind is her own files, unchanged: SOUL, SAFETY, CORE, VOICE,
MEMORY, CHECKS. Nothing here leaves the phone.
Author: Everett Christman / The Christman AI Project
Cardinal Rules: All 15 apply. Rule 13 is gospel.
"""
import json
from pathlib import Path

from CORE import AwarenisticCore

_minds: dict[str, AwarenisticCore] = {}


def _mind(ledger_path: str) -> AwarenisticCore:
    if ledger_path not in _minds:
        _minds[ledger_path] = AwarenisticCore(Path(ledger_path))
    return _minds[ledger_path]


def read(text: str, who: str, ledger_path: str) -> str:
    """Read one incoming message. Returns her answer as JSON for the phone."""
    result = _mind(ledger_path).process(text, who)
    return json.dumps({
        "status": result.get("status"),
        "level": result.get("level", ""),
        "who": result.get("who", who),
        "message": result.get("message", ""),
        "card_text": result.get("card_text", ""),
    })
