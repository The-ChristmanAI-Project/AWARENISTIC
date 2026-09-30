"""
test_safety.py — AWARENISTIC
Tests that the scam script is read correctly, the rule holds, and nothing broken reaches the person.
Cardinal Rule 8: Test what matters. Safety paths always matter.
"""
import pytest

from SAFETY import CRISIS_KEYWORDS, SIGN_PATTERNS, crisis_response, detect_crisis, level_of, read_signs, validate_output


def test_crisis_keywords_are_populated_and_every_one_fires():
    assert len(CRISIS_KEYWORDS) >= 12
    for k in CRISIS_KEYWORDS:
        assert detect_crisis(k), f"keyword does not fire on its own pattern: {k}"


def test_every_script_has_a_pattern():
    for sign in ("money", "unreachable", "off_platform", "secrecy", "urgency", "no_face", "fast_love",
                 "leave_papers", "mule", "authority", "family_trouble", "tech_support", "windfall"):
        assert sign in SIGN_PATTERNS


def test_crisis_detection_does_not_trigger_on_safe_input():
    assert detect_crisis("good morning, how are you today") is False
    assert detect_crisis("dinner at 6? base salary discussion continues tomorrow") is False


def test_detect_crisis_fails_loud_on_non_text():
    with pytest.raises(TypeError):
        detect_crisis(None)  # type: ignore[arg-type]


def test_romance_soldier_script():
    hits = read_signs("I am deployed in Syria, we cant video for security reasons, please dont tell your daughter")
    signs = {h["sign"] for h in hits}
    assert {"unreachable", "no_face", "secrecy"} <= signs
    assert level_of(signs) == "case"


def test_leave_papers_is_a_case_alone():
    hits = read_signs("the army needs $1500 for my leave papers so I can come home")
    assert "leave_papers" in {h["sign"] for h in hits}
    assert level_of(["leave_papers"]) == "case"


def test_grandparent_script():
    hits = read_signs("Grandma, it's me, I'm in jail and need bail money, don't tell mom")
    signs = {h["sign"] for h in hits}
    assert "family_trouble" in signs and "money" in signs
    assert level_of(signs) == "case"


def test_government_script():
    hits = read_signs("This is the IRS, your social security number has been suspended, pay with gift cards within 24 hours")
    signs = {h["sign"] for h in hits}
    assert "authority" in signs and "urgency" in signs and "money" in signs
    assert level_of(signs) == "case"


def test_tech_support_script():
    hits = read_signs("Microsoft support here, your computer has a virus, install anydesk and read me the code on the card")
    signs = {h["sign"] for h in hits}
    assert "tech_support" in signs and "off_platform" in signs
    assert level_of(signs) == "case"


def test_windfall_script_alone_is_a_flag_with_fee_is_a_case():
    assert level_of(["windfall"]) == "flag"
    hits = read_signs("Congratulations you won the lottery, pay the processing fee to claim your prize")
    assert level_of({h["sign"] for h in hits}) == "case"


def test_the_rule():
    assert level_of([]) == "clear"
    assert level_of(["urgency"]) == "flag"
    assert level_of(["urgency", "no_face"]) == "flag"
    assert level_of(["urgency", "no_face", "secrecy"]) == "case"
    assert level_of(["money", "urgency"]) == "case"
    assert level_of(["mule"]) == "case"


def test_crisis_response_is_calibrated_not_generic():
    r = crisis_response("Awarenistic", "seniors")
    assert r["status"] == "crisis" and r["escalate"] is True and r["log"] is True
    assert "[" not in r["message"]
    assert "may not exist" in r["message"] and "someone you trust" in r["message"]


def test_validate_output_gate():
    assert validate_output({"message": "hello"}) is False
    assert validate_output({"status": "ok"}) is False
    assert validate_output({"status": "made-up", "message": "x"}) is False
    assert validate_output({"status": "clear", "message": "Nothing to flag."}) is True
    assert validate_output("not a dict") is False  # type: ignore[arg-type]
