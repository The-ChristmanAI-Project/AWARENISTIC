"""
CHECKS.py — AWARENISTIC
Two real outside checks a stranger's number and address can be run against, each honest when it cannot run.
Author: Everett Christman / The Christman AI Project
Cardinal Rules: All 15 apply. Rule 13 is gospel. Rule 15: Twilio runs only on a key the person entered.
Version: 1.0.0
"""

import base64
import json
import logging
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from SOUL import BEING_NAME

logger = logging.getLogger(f"{BEING_NAME}.checks")

FREE_MAIL = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", "icloud.com",
    "protonmail.com", "proton.me", "mail.com", "yandex.com", "gmx.com", "zoho.com",
}
_PHONE = re.compile(r"(\+?\d[\d\s().-]{7,}\d)")
_MAIL = re.compile(r"[^\s@<>\"']+@[^\s@<>\"']+\.[^\s@<>\"']+")
TIMEOUT = 10


def clean_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) < 8 or len(digits) > 15:
        return ""
    return f"+{digits}" if (raw or "").strip().startswith("+") else digits


def phones_in(text: str) -> list[str]:
    out = []
    for m in _PHONE.finditer(text or ""):
        c = clean_phone(m.group(1))
        if c and c not in out:
            out.append(c)
    return out


def mails_in(text: str) -> list[str]:
    out = []
    for m in _MAIL.finditer(text or ""):
        a = m.group(0).lower()
        if a not in out:
            out.append(a)
    return out


def _get_json(url: str, headers: dict | None = None) -> tuple[int, dict | None]:
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": f"{BEING_NAME}/1.0",
                                               **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:  # noqa: BLE001 — reported, never hidden
        logger.warning("[%s] request failed for %s: %s", BEING_NAME, url, e)
        return 0, None


def check_phone(raw: str, account_sid: str, auth_token: str) -> dict:
    """
    Twilio Lookup v2 with line type. Runs ONLY with a key the person entered (Rule 15).
    Says 'not checked' plainly when it cannot run.
    """
    number = clean_phone(raw)
    if not number:
        return {"ok": False, "number": raw, "lines": ["That is not a phone number I can read."]}
    if not account_sid or not auth_token:
        return {"ok": False, "number": number,
                "lines": ["Not checked. No Twilio key has been entered. Enter one and press again."]}
    e164 = number if number.startswith("+") else f"+1{number[1:] if number.startswith('1') else number}"
    url = (f"https://lookups.twilio.com/v2/PhoneNumbers/{urllib.parse.quote(e164)}"
           f"?Fields=line_type_intelligence")
    token = base64.b64encode(f"{account_sid}:{auth_token}".encode()).decode()
    status, body = _get_json(url, {"Authorization": f"Basic {token}"})
    if status in (401, 403):
        return {"ok": False, "number": e164, "lines": ["Twilio refused the key. Check it and try again."]}
    if status == 404:
        return {"ok": True, "number": e164, "valid": False, "lines": ["Twilio says this number does not exist."]}
    if status != 200 or body is None:
        return {"ok": False, "number": e164, "lines": [f"Twilio did not answer. HTTP {status}."]}
    lti = body.get("line_type_intelligence") or {}
    ltype, carrier, country = lti.get("type"), lti.get("carrier_name"), body.get("country_code")
    said = {
        "mobile": "A mobile line.",
        "landline": "A landline.",
        "fixedVoip": "A VoIP line tied to an address, like a home internet phone.",
        "nonFixedVoip": "A VoIP line not tied to any address. Anyone anywhere can get one in a minute. "
                        "This is the kind scammers use.",
        "personal": "A personal number.", "tollFree": "A toll-free number.",
        "premium": "A premium-rate number.", "voicemail": "A voicemail-only number.",
        "unknown": "Twilio could not tell what kind of line it is.",
    }
    lines = ["Twilio says this number is not valid." if body.get("valid") is False else "The number is real."]
    if country:
        lines.append(f"Country: {country}.")
    if ltype:
        lines.append(said.get(ltype, f"Line type: {ltype}."))
    if carrier:
        lines.append(f"Carrier: {carrier}.")
    if ltype == "nonFixedVoip" and country == "US":
        lines.append("A US internet number is not a base overseas and is not a rig.")
    return {"ok": True, "number": e164, "valid": body.get("valid"), "line_type": ltype,
            "carrier": carrier, "country": country, "lines": lines}


def _dns(name: str, rtype: str) -> dict | None:
    status, body = _get_json(f"https://dns.google/resolve?name={urllib.parse.quote(name)}&type={rtype}",
                             {"Accept": "application/dns-json"})
    return body if status == 200 else None


def _registrable(domain: str) -> str:
    parts = [p for p in domain.split(".") if p]
    if len(parts) <= 2:
        return domain
    last2 = ".".join(parts[-2:])
    if re.match(r"^(co|com|org|net|gov|ac|edu)\.[a-z]{2}$", last2):
        return ".".join(parts[-3:])
    return last2


def check_mail(address: str) -> dict:
    """Public DNS and the domain registry (RDAP). No key. Says how old the domain is and whether it takes mail."""
    clean = (address or "").strip().lower()
    at = clean.rfind("@")
    if at < 1:
        return {"ok": False, "address": address, "domain": "", "lines": ["That is not a mail address I can read."]}
    domain = clean[at + 1:]
    root = _registrable(domain)
    lines: list[str] = []
    dot_mil, free = domain.endswith(".mil"), domain in FREE_MAIL
    if dot_mil:
        lines.append("A .mil address. That is the military's own mail system.")
    if free:
        lines.append(f"A free {domain} address. Anyone can make one in a minute. A serving soldier writes from .mil.")

    mx = _dns(domain, "MX")
    takes_mail = None
    if mx is None:
        lines.append("Could not reach public DNS to see whether the domain takes mail.")
    else:
        takes_mail = any(a.get("type") == 15 for a in mx.get("Answer", []) or [])
        lines.append("The domain takes mail." if takes_mail else "The domain has no mail server. Mail to it goes nowhere.")

    has_spf = None
    txt = _dns(domain, "TXT")
    if txt is not None and not free and not dot_mil:
        has_spf = any(a.get("type") == 16 and "v=spf1" in a.get("data", "").lower() for a in txt.get("Answer", []) or [])
        lines.append("It publishes an SPF record, so it says which servers may send as it." if has_spf
                     else "No SPF record. Anyone can send mail that claims to be from it.")

    registered, age_days = None, None
    if not free and not dot_mil:
        tld = root.rsplit(".", 1)[-1]
        rdap = (f"https://rdap.verisign.com/{tld}/v1/domain/{urllib.parse.quote(root)}" if tld in ("com", "net")
                else f"https://rdap.org/domain/{urllib.parse.quote(root)}")
        status, body = _get_json(rdap, {"Accept": "application/rdap+json"})
        if status == 200 and body:
            reg = next((e.get("eventDate") for e in body.get("events", []) if e.get("eventAction") == "registration"), None)
            if reg:
                registered = reg[:10]
                try:
                    age_days = (datetime.now(timezone.utc) - datetime.fromisoformat(reg.replace("Z", "+00:00"))).days
                except ValueError:
                    age_days = None
                if age_days is not None and age_days < 90:
                    lines.append(f"The domain {root} was registered {age_days} days ago ({registered}). Brand new domains are a scam tell.")
                elif age_days is not None and age_days < 365:
                    lines.append(f"The domain {root} is {round(age_days / 30)} months old (registered {registered}).")
                else:
                    lines.append(f"The domain {root} has been registered since {registered}.")
            else:
                lines.append(f"The registry did not say when {root} was registered.")
        elif status == 404:
            lines.append(f"No registry record for {root}. The domain may not be registered at all.")
        else:
            lines.append(f"The registry did not answer for {root}. HTTP {status}.")

    return {"ok": True, "address": clean, "domain": domain, "takes_mail": takes_mail, "has_spf": has_spf,
            "registered": registered, "age_days": age_days, "free_mail": free, "dot_mil": dot_mil, "lines": lines}
