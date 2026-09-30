"""
test_memory.py — AWARENISTIC
Tests that memory is real, on the person's own device, honest, and fails loud when broken.
Cardinal Rule 13: Never fabricate memory. Never invent history.
"""
import pytest

from MEMORY import BeingMemory


def test_remember_stores_event_in_session_and_on_disk(ledger):
    mem = BeingMemory("Awarenistic", ledger)
    mem.remember({"who": "James", "text": "hello"})
    assert len(mem.short_term) == 1 and mem.short_term[0]["text"] == "hello"
    assert ledger.exists() and "hello" in ledger.read_text(encoding="utf-8")


def test_remember_adds_timestamp(ledger):
    mem = BeingMemory("Awarenistic", ledger)
    mem.remember({"who": "x", "text": "y"})
    assert "timestamp" in mem.short_term[0]


def test_remember_fails_loud_on_bad_event(ledger):
    mem = BeingMemory("Awarenistic", ledger)
    with pytest.raises(TypeError):
        mem.remember("not a dict")  # type: ignore[arg-type]


def test_remember_fails_loud_when_disk_is_broken(tmp_path):
    mem = BeingMemory("Awarenistic", tmp_path)  # a directory, not a file — the write must fail
    with pytest.raises(RuntimeError):
        mem.remember({"who": "x", "text": "y"})


def test_recall_returns_what_exists_and_nothing_else(ledger):
    mem = BeingMemory("Awarenistic", ledger)
    mem.remember({"who": "James", "text": "gift cards"})
    mem.remember({"who": "Misty", "text": "dinner"})
    assert [e["who"] for e in mem.recall("james")] == ["James"]
    assert mem.recall("nobody") == []


def test_recall_survives_forget_session_via_ledger(ledger):
    mem = BeingMemory("Awarenistic", ledger)
    mem.remember({"who": "James", "text": "gift cards"})
    mem.forget_session()
    assert mem.short_term == []
    assert len(mem.recall("james")) == 1


def test_recall_rejects_empty_query(ledger):
    with pytest.raises(ValueError):
        BeingMemory("Awarenistic", ledger).recall("")


def test_thread_is_one_stranger_oldest_first(ledger):
    mem = BeingMemory("Awarenistic", ledger)
    mem.remember({"who": "James", "text": "first"})
    mem.remember({"who": "Pat", "text": "other"})
    mem.remember({"who": "James", "text": "second"})
    t = mem.thread("james")
    assert [e["text"] for e in t] == ["first", "second"]
