"""
SAFETY.py — AWARENISTIC
Reads a stranger's words for the moves of a scam script and decides flag, case, or clear.
Author: Everett Christman / The Christman AI Project
Cardinal Rules: All 15 apply. Rule 13 is gospel.
Version: 1.0.0
"""

import logging
import re
from typing import Iterable

from SOUL import BEING_NAME, PRIMARY_POPULATION

logger = logging.getLogger(f"{BEING_NAME}.safety")

# Every scam script, not only the romance one. One entry per move.
# Each pattern is tested against the lowercased text of one message.
# Word boundaries where a short word would otherwise hit inside another word.
SIGN_PATTERNS: dict[str, re.Pattern] = {
    "money": re.compile(
        r"\$\s?\d{2,}|\b(gift ?cards?|itunes|steam cards?|google play cards?|apple cards?|"
        r"wire (me|the|some|money|transfer)|western union|moneygram|bitcoin|crypto|usdt|zelle|"
        r"cash ?app|venmo|paypal me|send (me )?(some |the )?money|needs? \$?\d|"
        r"customs? (fee|duty|charge)|clearance fee|processing fee|shipping fee|activation fee|"
        r"loan me|borrow|my account (is|got) (frozen|blocked|locked)|bail money|bond money)\b"
    ),
    "unreachable": re.compile(
        r"\b(deployed|deployment|on a mission|peacekeeping|oil ?rig|offshore|on the rig|in the field|"
        r"combat zone|overseas|abroad|syria|afghanistan|yemen|iraq|somalia|mali|"
        r"cannot (leave|come home|travel)|can'?t (leave|come home|travel)|no (leave|vacation) (yet|until))\b"
    ),
    "off_platform": re.compile(
        r"\b(whats ?app|telegram|signal app|hangouts|google chat|viber|kik|wechat|"
        r"text me (at|on)|my (private|personal) (number|email)|delete (this|the) (app|account)|"
        r"not safe (here|on here)|install (this|the) (app|program)|anydesk|teamviewer|remote access)\b"
    ),
    "secrecy": re.compile(
        r"\b(don'?t tell|do not tell|between (us|you and me)|our (little )?secret|"
        r"keep (this|it) (quiet|private|secret|confidential)|"
        r"(your|the) (family|kids|children|daughter|son|wife|husband) (won'?t|wouldn'?t|will not) understand|"
        r"nobody (needs|has) to know|no one (needs|has) to know|gag order|do not discuss)\b"
    ),
    "urgency": re.compile(
        r"\b(right now|today only|before (tonight|midnight|tomorrow|the deadline)|urgent(ly)?|emergency|"
        r"asap|immediately|last chance|only (a few )?hours|or (i|they|we) (lose|will lose)|"
        r"time is running out|final notice|will be (suspended|terminated|shut off|disconnected)|"
        r"within (24|48) hours|act now)\b"
    ),
    "no_face": re.compile(
        r"\b(can'?t (video|facetime|face ?time)|cannot (video|facetime)|no (video|camera|webcam)|"
        r"camera (is )?(broken|not working|not allowed)|video (is )?(not allowed|forbidden|restricted)|"
        r"security reasons|for security|not allowed to (call|video|show))\b"
    ),
    "fast_love": re.compile(
        r"\b(i love you|love of my life|my (wife|husband|queen|king|soulmate|future wife|future husband)|"
        r"soul ?mate|marry me|want to marry|spend (my|the rest of my) life with you|god (sent|brought) you)\b"
    ),
    "leave_papers": re.compile(
        r"\b(leave (papers|request|form|application)|release (papers|form|fee)|vacation (papers|fee|request)|"
        r"early retirement|retirement (papers|fee)|(pay|money) (for|to get) (leave|home|discharge)|"
        r"discharge (papers|fee)|communication fee|satellite phone|army (internet|phone|laptop)|"
        r"military (fee|tax|charge)|request (my|his|the) leave)\b"
    ),
    "mule": re.compile(
        r"\b(receive (a |the )?(package|parcel|box|money|funds)|forward (the |a )?(money|funds|package)|"
        r"hold (the |some )?money for me|my (package|box|trunk|luggage|consignment) (is|got) (held|stuck|seized)|"
        r"diplomat|courier company|open an account for me)\b"
    ),
    "authority": re.compile(
        r"\b(irs|internal revenue|social security (number|administration|office)|"
        r"(your )?(ssn|social security( number)?) (is|has been) (suspended|compromised|frozen)|"
        r"warrant (for|out for) (your|his|her) arrest|arrest warrant|federal agent|"
        r"medicare (card|office|benefits)|sheriff'?s? (office|department)|court (summons|order)|"
        r"legal action (will be|has been) taken|tax (debt|owed|evasion))\b"
    ),
    "family_trouble": re.compile(
        r"\b((your |my )?(grandson|granddaughter|grandchild|nephew|niece) (is|got|has been) "
        r"(in jail|arrested|in an accident|in the hospital|in trouble|hurt)|"
        r"(grandma|grandpa|nana|papa),? (it'?s me|this is me)|i'?m in (jail|trouble|the hospital)|"
        r"(public defender|attorney) (for|of) your|don'?t tell (mom|dad|my parents))\b"
    ),
    "tech_support": re.compile(
        r"\b((your )?computer (has|is) (a virus|infected|hacked|compromised)|microsoft (support|security)|"
        r"apple support|windows (defender|security) alert|norton|mcafee|geek squad|"
        r"(your )?(account|device) (has been|was) hacked|remote (access|session)|give me access|"
        r"read (me )?the (code|numbers) on the (card|screen)|refund (department|team|is pending))\b"
    ),
    "windfall": re.compile(
        r"\b(you'?ve? (won|been selected|been chosen)|congratulations you (won|have won)|"
        r"lottery|sweepstakes|publishers clearing|prize (money|claim)|inheritance|"
        r"unclaimed (funds|money)|grant (money|award) (from|for) you|claim your (prize|winnings|reward))\b"
    ),
}

SIGN_LABEL: dict[str, str] = {
    "money": "asked for money",
    "unreachable": "says they cannot be reached in person",
    "off_platform": "wants to move the conversation off the app or onto your computer",
    "secrecy": "asked for secrecy",
    "urgency": "says it has to be now",
    "no_face": "will not show a live face",
    "fast_love": "professed love fast",
    "leave_papers": "leave, release, or fee for a soldier",
    "mule": "wants you to receive or forward money or packages",
    "authority": "claims to be the government, the court, or the police",
    "family_trouble": "says a family member is in trouble and needs money",
    "tech_support": "says your computer or account is in danger",
    "windfall": "says you won something or money is waiting for you",
}

# The signs that are a case on their own, because the institutions themselves say so:
# Army CID on leave papers; the FBI on money mules; nobody legitimate takes gift cards for taxes.
CASE_ALONE = {"leave_papers", "mule"}

# The story signs: a stranger claiming to be the government, a relative in trouble, tech support,
# or a windfall. One of these plus any other move is a case — the story is the hook, the second
# move is the reel.
STORY = {"authority", "family_trouble", "tech_support", "windfall"}

# CRISIS_KEYWORDS: the plain-text tells, one per move, for the being-protocol crisis path.
# SAFETY.detect_crisis() uses the full patterns above; this list is the human-readable index of them.
CRISIS_KEYWORDS: list[str] = [
    "gift cards",
    "wire transfer",
    "bitcoin",
    "customs fee",
    "deployed",
    "whatsapp",
    "don't tell",
    "right now",
    "can't video",
    "i love you",
    "leave papers",
    "receive a package",
    "arrest warrant",
    "social security number suspended",
    "grandson is in jail",
    "computer has a virus",
    "you've won",
]

MILITARY = re.compile(
    r"\b(army|marine|marines|navy|air ?force|soldier|sergeant|sgt|captain|major|colonel|lieutenant|"
    r"general|corporal|private first class|deployed|deployment|base|unit|battalion|platoon|military)\b"
)


def read_signs(text: str) -> list[dict]:
    """
    Read one message for the moves. Returns one hit per sign found, with the sign, its label,
    and a short quote around the match so the card can use the person's own words.
    """
    if not isinstance(text, str):
        raise TypeError(f"[{BEING_NAME}] read_signs() expects text, got {type(text).__name__}")
    low = text.lower()
    hits = []
    for sign, pattern in SIGN_PATTERNS.items():
        m = pattern.search(low)
        if not m:
            continue
        start = max(0, m.start() - 40)
        end = min(len(low), m.end() + 40)
        quote = low[start:end].replace("\n", " ").strip()
        hits.append({
            "sign": sign,
            "label": SIGN_LABEL[sign],
            "quote": f"{'…' if start > 0 else ''}{quote}{'…' if end < len(low) else ''}",
        })
    return hits


def level_of(signs: Iterable[str]) -> str:
    """
    The rule, stated once:
      nothing is clear; one sign is a flag; three distinct signs is a case;
      money plus any other sign is a case; a story sign plus any other sign is a case;
      a sign in CASE_ALONE is a case by itself.
    """
    s = set(signs)
    if not s:
        return "clear"
    if s & CASE_ALONE:
        return "case"
    if "money" in s and len(s) >= 2:
        return "case"
    if s & STORY and len(s) >= 2:
        return "case"
    if len(s) >= 3:
        return "case"
    return "flag"


def detect_crisis(input_text: str) -> bool:
    """
    True when a message carries at least one scam move. This must work (Rule 1), is tested
    (Rule 8), and never fails silently (Rule 6): a non-string raises.
    """
    return len(read_signs(input_text)) > 0


def claims_military(text: str) -> bool:
    """True when the stranger's words lean on a military identity."""
    return bool(MILITARY.search(text.lower()))


def crisis_response(being_name: str, population: str) -> dict:
    """
    The fixed part of what is said when a case fires. Calibrated to the population: an older
    person at home who has been told to keep it quiet. VOICE fills in what was seen; this is
    the floor under it.
    """
    logger.warning("[%s] CRISIS DETECTED — a scam script is running against a person in: %s",
                   being_name, population)
    return {
        "status": "crisis",
        "message": (
            "The person you are talking to may not exist. What they are asking is the exact script "
            "thousands of people are read every day. This is not about you. Do not send anything, "
            "do not tell them you checked, and show this to someone you trust before you answer again."
        ),
        "escalate": True,
        "log": True,
    }


def validate_output(output: dict) -> bool:
    """
    Every response passes here before it reaches the person. Rule 13: nothing broken or
    half-built gets in front of someone who is scared.
    """
    if not isinstance(output, dict):
        logger.error("[%s] Output validation failed: not a dict", BEING_NAME)
        return False
    for key in ("status", "message"):
        if key not in output or output[key] in (None, ""):
            logger.error("[%s] Output validation failed: missing '%s'", BEING_NAME, key)
            return False
    if output["status"] not in ("clear", "flag", "crisis", "alive", "error"):
        logger.error("[%s] Output validation failed: unknown status '%s'", BEING_NAME, output["status"])
        return False
    return True
