"""
VOICE.py — AWARENISTIC
Writes the card the person reads: what I saw, what it means, what to do now, in their words.
Author: Everett Christman / The Christman AI Project
Cardinal Rules: All 15 apply. Rule 13 is gospel.
Version: 1.0.0
"""

from SOUL import BEING_NAME, TONE_CRISIS, TONE_DEFAULT
from SAFETY import SIGN_LABEL

# The Army's own investigators (Army CID) publish what a real soldier never needs.
# Quoted to the person, attributed to the Army, never claimed as our own verification.
ARMY_NEVER = [
    "Soldiers and their families are not charged money for a soldier to go on leave.",
    "Nobody has to request leave on a soldier's behalf, and no general writes to you about it.",
    "Soldiers are not charged money or taxes to communicate, to marry, or to retire early.",
    "Soldiers have medical insurance; their friends do not pay their medical bills.",
    "Deployed soldiers do not need the public's money to eat, to phone home, or to fly home.",
    "Deployed soldiers do not find large sums of money and need your help moving it.",
]

# What the institutions themselves say, one line per story, so the card never argues, it quotes.
STORY_TRUTH = {
    "authority": "The IRS, Social Security, Medicare, and the courts do not call to demand payment, "
                 "do not take gift cards or wire transfers, and do not threaten arrest by phone.",
    "family_trouble": "A real emergency does not come with a rule that you cannot call the rest of the family. "
                      "Hang up and call your grandchild directly, at the number you already have.",
    "tech_support": "Microsoft, Apple, and your bank do not call you first, do not ask for remote access, "
                    "and never ask you to read them numbers off a gift card.",
    "windfall": "You cannot win a lottery you did not enter, and a real prize never costs a fee to collect.",
}

SOURCES = [
    {"label": "Report it to the FTC", "url": "https://reportfraud.ftc.gov/"},
    {"label": "Report it to the FBI (IC3)", "url": "https://www.ic3.gov/"},
]


def _who(name: str) -> str:
    return (name or "").strip() or "this person"


def build_card(who: str, level: str, hits: list[dict], contacts: int, military: bool,
               phones: list[str], mails: list[str]) -> dict:
    """
    The three-line card. Speaks to the person being worked, never to the owner of the machine,
    never to the stranger. Tone is calm_and_direct on a case, steady otherwise.
    """
    if level not in ("clear", "flag", "case"):
        raise ValueError(f"[{BEING_NAME}] build_card() got unknown level '{level}'")
    name = _who(who)
    signs = []
    for h in hits:
        if h["sign"] not in signs:
            signs.append(h["sign"])

    saw = []
    for sign in signs:
        first = next(h for h in hits if h["sign"] == sign)
        saw.append(f'{name} {SIGN_LABEL[sign]}: "{first["quote"]}"' if first.get("quote")
                   else f"{name} {SIGN_LABEL[sign]}.")
    civilian_mail = [m for m in mails if not m.endswith(".mil")]
    if military and civilian_mail:
        saw.append(f"{name} says military but writes from {', '.join(civilian_mail)}. "
                   "Serving members have a .mil address.")

    means = []
    if level == "case":
        means.append(f"These are the moves of a person who does not exist. Not a guess about {name}. "
                     "A match against the script that thousands of people are read every day.")
        means.append("This is not about you. The script is the same for everyone it is sent to.")
    elif level == "flag":
        means.append("One of the moves of a known scam. On its own it proves nothing. "
                     "Watch for a second one, especially money.")
    else:
        means.append("Nothing on the record matches a known scam move.")
    for sign in signs:
        if sign in STORY_TRUTH:
            means.append(STORY_TRUTH[sign])
    if military:
        means.append("The Army's own investigators say a real soldier never needs any of this:")
        means.extend(f"  {line}" for line in ARMY_NEVER)

    do_now = []
    if level != "clear":
        do_now.append("Do not send anything. Not money, not cards, not a photo of your ID.")
        do_now.append(f"Do not tell {name} you checked.")
        do_now.append("Show this card to someone you trust before you answer again.")
        if phones:
            do_now.append("Press Check the number to see what kind of line it is.")
        if mails:
            do_now.append("Press Check the address to see how old the sender's domain is and whether it takes mail.")
        if level == "case":
            do_now.append("Report it. It takes five minutes and it is how these get shut down.")

    heading = {
        "case": f"{name} may not exist.",
        "flag": f"One thing about {name} to watch.",
        "clear": f"Nothing to flag about {name}.",
    }[level]

    return {
        "heading": heading,
        "tone": TONE_CRISIS if level == "case" else TONE_DEFAULT,
        "saw": saw,
        "means": means,
        "do_now": do_now,
        "sources": SOURCES if level != "clear" else [],
        "contacts": contacts,
    }


def card_text(card: dict) -> str:
    """Plain text of the card, for reading aloud and for the trusted person."""
    lines = [f"From {BEING_NAME}.", "", card["heading"], "  What it saw:"]
    lines.extend(f"    {s}" for s in card["saw"]) if card["saw"] else lines.append("    nothing")
    lines.append("  What it means:")
    lines.extend(f"    {s.strip()}" for s in card["means"])
    if card["do_now"]:
        lines.append("  What to do now:")
        lines.extend(f"    {s}" for s in card["do_now"])
    for s in card["sources"]:
        lines.append(f"  {s['label']}: {s['url']}")
    return "\n".join(lines)
