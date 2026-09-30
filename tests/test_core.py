"""
test_core.py — AWARENISTIC
Tests that the being wakes, routes the script to safety, builds the card from the whole thread,
and the local door on 3600 answers. Cardinal Rule 1: It has to actually work.
"""
import pytest
from fastapi.testclient import TestClient

from CORE import AwarenisticCore
from SAFETY import CRISIS_KEYWORDS, validate_output


def test_core_initializes(ledger):
    core = AwarenisticCore(ledger)
    assert core.identity["name"] == "Awarenistic"


def test_core_routes_crisis_to_safety(ledger):
    core = AwarenisticCore(ledger)
    r = core.process("the army needs $1500 for my leave papers", who="James")
    assert r["status"] == "crisis" and r["escalate"] is True and r["level"] == "case"
    assert r["card"]["heading"] == "James may not exist."


def test_core_uses_a_real_crisis_keyword(ledger):
    core = AwarenisticCore(ledger)
    r = core.process(CRISIS_KEYWORDS[0], who="Pat")
    assert r["status"] in ("flag", "crisis")


def test_core_builds_the_case_across_the_thread(ledger):
    core = AwarenisticCore(ledger)
    first = core.process("hi beautiful, I am a sergeant deployed overseas", who="James")
    assert first["level"] == "flag"
    second = core.process("we cant video for security reasons, keep this between us", who="James")
    assert second["level"] == "case" and second["status"] == "crisis"
    assert second["card"]["contacts"] == 2
    assert any(".mil" not in line and "military" in line.lower() or "Army" in line for line in second["card"]["means"])


def test_core_clear_on_a_plain_message(ledger):
    core = AwarenisticCore(ledger)
    r = core.process("dinner at 6?", who="Misty")
    assert r["status"] == "clear" and validate_output(r)


def test_core_refuses_empty_text(ledger):
    r = AwarenisticCore(ledger).process("   ")
    assert r["status"] == "error"


def test_core_asks_the_soul(ledger):
    core = AwarenisticCore(ledger)
    assert core.may_i("reply to the scammer")["allowed"] is False
    assert core.may_i("show the card to the person")["allowed"] is True


def test_every_output_passes_the_gate(ledger):
    core = AwarenisticCore(ledger)
    for text in ("hello", "send me $500 in gift cards", "you've won the lottery"):
        assert validate_output(core.process(text, who="X"))


def test_api_health_and_door(ledger, monkeypatch):
    monkeypatch.setenv("AWARENISTIC_LEDGER", str(ledger))
    import importlib
    import MEMORY, API  # noqa: E401
    importlib.reload(MEMORY)
    importlib.reload(API)
    c = TestClient(API.app)
    assert c.get("/health").json() == {"status": "alive", "being": "Awarenistic"}
    assert API.PORT == 3600 and API.HOST == "127.0.0.1"
    r = c.post("/message", json={"text": "I need $800 in gift cards, dont tell your daughter", "who": "James"})
    assert r.status_code == 200 and r.json()["level"] == "case"
    assert c.post("/message", json={"text": ""}).status_code == 422
    assert c.post("/keys", json={"twilio_account_sid": "", "twilio_auth_token": ""}).json()["twilio_seated"] is False
    assert c.post("/check/phone", json={"number": "419-744-0419"}).json()["lines"][0].startswith("Not checked")
