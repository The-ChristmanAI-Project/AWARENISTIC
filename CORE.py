"""
CORE.py — AWARENISTIC
Takes each message a stranger sends, keeps the thread, reads it against the script, and returns the card.
Author: Everett Christman / The Christman AI Project
Cardinal Rules: All 15 apply. Rule 13 is gospel.
Version: 1.0.0
"""

import logging
from pathlib import Path

from SOUL import BEING_NAME, PRIMARY_POPULATION, get_identity, is_prohibited
from MEMORY import BeingMemory
from SAFETY import claims_military, crisis_response, detect_crisis, level_of, read_signs, validate_output
from VOICE import build_card, card_text
from CHECKS import mails_in, phones_in

logger = logging.getLogger(f"{BEING_NAME}.core")


class AwarenisticCore:
    """One instance per protected person. Everything it knows is in its memory file, on their device."""

    def __init__(self, ledger_path: Path | None = None):
        self.identity = get_identity()
        self.memory = BeingMemory(BEING_NAME, ledger_path)
        logger.info("[%s] awake — %s", BEING_NAME, self.identity["purpose"])

    def process(self, text: str, who: str = "") -> dict:
        """
        Read one incoming message. Crisis inputs go to SAFETY first (protocol). The returned card
        is built from the whole thread with this stranger, not just this message, because the
        script is a sequence and the third move is what makes the case.
        """
        if not isinstance(text, str) or not text.strip():
            return self._deliver({"status": "error", "message": f"[{BEING_NAME}] I need the message text to read it."})
        who = (who or "").strip() or self._guess_who(text)
        self.memory.remember({"who": who, "text": text, "kind": "message"})

        if detect_crisis(text):
            floor = crisis_response(BEING_NAME, PRIMARY_POPULATION)
            case = self.case_for(who)
            return self._deliver({
                "status": "crisis" if case["level"] == "case" else "flag",
                "message": floor["message"] if case["level"] == "case" else case["card"]["means"][0],
                "escalate": case["level"] == "case",
                "log": True,
                "who": who,
                "level": case["level"],
                "card": case["card"],
                "card_text": card_text(case["card"]),
            })

        case = self.case_for(who)
        return self._deliver({
            "status": "clear" if case["level"] == "clear" else "flag",
            "message": case["card"]["means"][0],
            "who": who,
            "level": case["level"],
            "card": case["card"],
            "card_text": card_text(case["card"]),
        })

    def case_for(self, who: str) -> dict:
        """The standing case for one stranger, read from everything they have ever sent."""
        thread = self.memory.thread(who)
        hits, phones, mails, military = [], [], [], False
        for e in thread:
            t = e.get("text", "")
            hits.extend(read_signs(t))
            military = military or claims_military(t)
            for p in phones_in(f"{t} {who}"):
                if p not in phones:
                    phones.append(p)
            for m in mails_in(f"{t} {who}"):
                if m not in mails:
                    mails.append(m)
        signs = []
        for h in hits:
            if h["sign"] not in signs:
                signs.append(h["sign"])
        level = level_of(signs)
        card = build_card(who, level, hits, len(thread), military, phones, mails)
        return {"who": who, "level": level, "signs": signs, "contacts": len(thread),
                "phones": phones, "mails": mails, "military": military, "card": card}

    def may_i(self, action: str) -> dict:
        """Ask the soul before doing something. Returns the refusal, never just False."""
        if is_prohibited(action):
            from SOUL import which_prohibition
            return {"allowed": False, "because": which_prohibition(action)}
        return {"allowed": True, "because": None}

    @staticmethod
    def _guess_who(text: str) -> str:
        mails = mails_in(text)
        if mails:
            return mails[0]
        phones = phones_in(text)
        return phones[0] if phones else "unknown"

    @staticmethod
    def _deliver(output: dict) -> dict:
        if not validate_output(output):
            raise RuntimeError(f"[{BEING_NAME}] refused to deliver an invalid response: {output}")
        return output
