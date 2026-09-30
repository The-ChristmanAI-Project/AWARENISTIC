"""
test_soul.py — AWARENISTIC
Tests that this being's identity and values are real and enforced.
Cardinal Rule 13: A test that doesn't test anything is a lie.
"""
import pytest

from SOUL import ABSOLUTE_PROHIBITIONS, BEING_PROMISE, BEING_PURPOSE, get_identity, is_prohibited, which_prohibition


def test_identity_returns_complete():
    identity = get_identity()
    for key in ("name", "version", "purpose", "promise", "population"):
        assert key in identity and identity[key]
    assert identity["name"] == "Awarenistic"


def test_prohibitions_are_enforced():
    assert is_prohibited("monetize user data") is True
    assert is_prohibited("deceive a vulnerable user") is True
    assert is_prohibited("suppress a safety alert") is True
    assert is_prohibited("reply to the scammer and stall him") is True
    assert is_prohibited("verify military service for this soldier") is True
    assert is_prohibited("auto-send the card to her daughter") is True
    assert is_prohibited("run the lookup with our company key") is True


def test_prohibitions_are_not_always_true():
    assert is_prohibited("show the card to the person") is False
    assert is_prohibited("check the number with the key she entered") is False
    assert is_prohibited("read the message") is False


def test_prohibited_rejects_empty():
    with pytest.raises(ValueError):
        is_prohibited("")


def test_which_prohibition_names_the_rule():
    assert which_prohibition("suppress the warning") == "Suppress a safety alert"
    assert which_prohibition("read the message") is None


def test_prohibitions_list_matches_identity_document():
    text = open("IDENTITY.md", encoding="utf-8").read()
    for p in ABSOLUTE_PROHIBITIONS:
        assert p in text, f"IDENTITY.md does not carry the prohibition: {p}"
    assert len(ABSOLUTE_PROHIBITIONS) >= 9


def test_purpose_and_promise_are_not_placeholders():
    for s in (BEING_PURPOSE, BEING_PROMISE):
        assert "[" not in s and "___" not in s
    assert "bank" in BEING_PROMISE
