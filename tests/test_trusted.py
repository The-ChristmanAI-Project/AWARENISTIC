"""
test_trusted.py — AWARENISTIC
The trusted-contact organ: a real card from her real mind, routed to the person they named.
She writes it and says where it goes. She never sends it, and it never goes to the stranger.
Author: Everett Christman / The Christman AI Project
Cardinal Rules: All 15 apply. Rule 13 is gospel.
"""
from CORE import AwarenisticCore
from VOICE import to_trusted


def _case_card(ledger):
    core = AwarenisticCore(ledger)
    core.process("hi beautiful, I am a sergeant deployed overseas", who="James")
    r = core.process("we cant video for security reasons, keep this between us", who="James")
    assert r["level"] == "case"
    return r["card"]


def test_a_phone_number_becomes_a_text_with_her_card(ledger):
    card = _case_card(ledger)
    route = to_trusted("(614) 555-0100", card, who="James")
    assert route["ok"] is True and route["kind"] == "text"
    assert route["to"] == "6145550100"
    assert route["body"].startswith("From Awarenistic.")
    assert "James may not exist." in route["body"]


def test_an_address_becomes_a_mail_with_the_heading_as_subject(ledger):
    card = _case_card(ledger)
    route = to_trusted("Misty@Example.com", card, who="James")
    assert route["ok"] is True and route["kind"] == "mail"
    assert route["to"] == "misty@example.com"
    assert route["subject"] == "Please read this: James may not exist."


def test_no_one_named_is_said_out_loud(ledger):
    route = to_trusted("", _case_card(ledger), who="James")
    assert route["ok"] is False and "No one you trust" in route["reason"]


def test_nonsense_is_refused_not_guessed(ledger):
    route = to_trusted("my daughter", _case_card(ledger), who="James")
    assert route["ok"] is False and "not a phone number" in route["reason"]


def test_a_clear_card_is_not_sent_to_anyone(ledger):
    core = AwarenisticCore(ledger)
    r = core.process("dinner at 6?", who="Misty")
    assert r["level"] == "clear"
    route = to_trusted("6145550100", r["card"], who="Misty")
    assert route["ok"] is False


def test_it_never_goes_to_the_stranger_on_the_card(ledger):
    core = AwarenisticCore(ledger)
    who = "+1 202 555 0147 · WhatsApp"
    core.process("hi dear, I am a soldier deployed overseas", who=who)
    r = core.process("I need $800 in gift cards for my leave papers", who=who)
    assert r["level"] == "case"
    route = to_trusted("+12025550147", r["card"], who=who)
    assert route["ok"] is False and "never goes to them" in route["reason"]
    mail_who = "sgt.james@gmail.com"
    core.process("I am a sergeant deployed overseas", who=mail_who)
    r2 = core.process("send $500 in gift cards for my leave papers", who=mail_who)
    route2 = to_trusted("SGT.James@gmail.com", r2["card"], who=mail_who)
    assert route2["ok"] is False and "never goes to them" in route2["reason"]


def test_the_soul_still_forbids_sending_without_the_persons_hand(ledger):
    core = AwarenisticCore(ledger)
    assert core.may_i("automatically send the card to the trusted contact")["allowed"] is False
