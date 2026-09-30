"""
MEMORY.py — AWARENISTIC
Keeps every stranger's messages together on this device, in a plain file the person owns.
Author: Everett Christman / The Christman AI Project
Cardinal Rules: All 15 apply. Rule 13 is gospel.
Version: 1.0.0
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from SOUL import BEING_NAME

logger = logging.getLogger(f"{BEING_NAME}.memory")

# Where the long-term record lives. A JSON-lines file next to the being, on the person's device.
# Never a server, never the company. Override with AWARENISTIC_LEDGER if the person wants it elsewhere.
DEFAULT_LEDGER = Path(os.getenv("AWARENISTIC_LEDGER", "awarenistic-ledger.jsonl"))


class BeingMemory:
    """Short-term is this session. Long-term is the ledger file. Both are real."""

    def __init__(self, being_name: str = BEING_NAME, ledger_path: Path | None = None):
        self.being_name = being_name
        self.short_term: list[dict] = []
        self.ledger_path = Path(ledger_path) if ledger_path else DEFAULT_LEDGER
        self.session_start = datetime.now(timezone.utc)

    def remember(self, event: dict) -> None:
        """Store something that just happened, in session and on disk. Fails loud (Rule 6)."""
        if not isinstance(event, dict):
            raise TypeError(f"[{self.being_name}] remember() needs a dict, got {type(event).__name__}")
        event = dict(event)
        event["timestamp"] = datetime.now(timezone.utc).isoformat()
        try:
            self.short_term.append(event)
            with self.ledger_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(event, ensure_ascii=False) + "\n")
        except Exception as e:  # noqa: BLE001 — re-raised with context, never swallowed
            logger.error("[%s] Memory write failed: %s", self.being_name, e, exc_info=True)
            raise RuntimeError(f"[{self.being_name}] Memory write failed: {e}") from e

    def recall(self, query: str) -> list[dict]:
        """
        Return every stored event whose 'who' or 'text' contains the query, session first,
        then the ledger. Returns what exists. Rule 13: never invents what does not.
        """
        if not isinstance(query, str) or not query.strip():
            raise ValueError(f"[{self.being_name}] recall() needs a non-empty query")
        q = query.lower()
        found = [e for e in self.short_term if self._matches(e, q)]
        seen = {json.dumps(e, sort_keys=True) for e in found}
        if self.ledger_path.exists():
            try:
                with self.ledger_path.open("r", encoding="utf-8") as fh:
                    for line in fh:
                        line = line.strip()
                        if not line:
                            continue
                        e = json.loads(line)
                        key = json.dumps(e, sort_keys=True)
                        if key not in seen and self._matches(e, q):
                            found.append(e)
                            seen.add(key)
            except Exception as e:  # noqa: BLE001
                logger.error("[%s] Memory read failed: %s", self.being_name, e, exc_info=True)
                raise RuntimeError(f"[{self.being_name}] Memory read failed: {e}") from e
        return found

    def thread(self, who: str) -> list[dict]:
        """Every message on record from one stranger, oldest first."""
        return sorted((e for e in self.recall(who) if e.get("who", "").lower() == who.lower()),
                      key=lambda e: e.get("timestamp", ""))

    def forget_session(self) -> None:
        """Clear short-term memory completely. The ledger on disk is the person's and stays."""
        self.short_term = []

    @staticmethod
    def _matches(event: dict, q: str) -> bool:
        return q in str(event.get("who", "")).lower() or q in str(event.get("text", "")).lower()
