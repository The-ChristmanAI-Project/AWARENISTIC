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
from VOICE import to_trusted

_minds: dict[str, AwarenisticCore] = {}


def _mind(ledger_path: str) -> AwarenisticCore:
    if ledger_path not in _minds:
        _minds[ledger_path] = AwarenisticCore(Path(ledger_path))
    return _minds[ledger_path]


def read(text: str, who: str, ledger_path: str, trusted: str = "") -> str:
    """
    Read one incoming message. Returns her answer as JSON for the phone, with where her card
    would go to the person they trust. She never sends it; the phone opens their own app.
    """
    result = _mind(ledger_path).process(text, who)
    card = result.get("card") or {}
    route = to_trusted(trusted, card, result.get("who", who)) if card else {"ok": False, "reason": ""}
    return json.dumps({
        "status": result.get("status"),
        "level": result.get("level", ""),
        "who": result.get("who", who),
        "message": result.get("message", ""),
        "card_text": result.get("card_text", ""),
        "trusted": route,
    })


def route_for(who: str, ledger_path: str, trusted: str) -> str:
    """
    Where the standing card for one stranger would go to the person they trust, read fresh from
    the whole thread on the phone. Used when the person opens a card she raised earlier.
    """
    case = _mind(ledger_path).case_for(who)
    return json.dumps(to_trusted(trusted, case["card"], who))
