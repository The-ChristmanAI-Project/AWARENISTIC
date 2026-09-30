"""
API.py — AWARENISTIC
The local door on the person's device: messages in, the card out, checks on request, keys in memory only.
Author: Everett Christman / The Christman AI Project
Cardinal Rules: All 15 apply. Rule 13 is gospel. Rule 12: binds 127.0.0.1, never 0.0.0.0.
Version: 1.0.0
"""

import logging
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from SOUL import BEING_NAME, get_identity
from CORE import AwarenisticCore
from CHECKS import check_mail, check_phone

logger = logging.getLogger(f"{BEING_NAME}.api")

# Everett's rule: keys go in a box in the interface, not a file. They live here, in memory, for
# this run only. Nothing writes them to disk. The port has a default so nothing has to be edited.
HOST = "127.0.0.1"
PORT = int(os.getenv("AWARENISTIC_PORT", "3600"))
_KEYS = {"twilio_account_sid": "", "twilio_auth_token": ""}

app = FastAPI(title=BEING_NAME, version=get_identity()["version"])
core = AwarenisticCore()


class Message(BaseModel):
    text: str = Field(min_length=1, max_length=20000)
    who: str = Field(default="", max_length=200)


class Keys(BaseModel):
    twilio_account_sid: str = Field(default="", max_length=64)
    twilio_auth_token: str = Field(default="", max_length=128)


class Number(BaseModel):
    number: str = Field(min_length=8, max_length=32)


class Address(BaseModel):
    address: str = Field(min_length=3, max_length=254)


@app.get("/health")
def health() -> dict:
    return {"status": "alive", "being": BEING_NAME}


@app.get("/identity")
def identity() -> dict:
    return get_identity()


@app.post("/message")
def message(m: Message) -> dict:
    return core.process(m.text, m.who)


@app.get("/case/{who}")
def case(who: str) -> dict:
    if not who.strip():
        raise HTTPException(status_code=422, detail="who is required")
    return core.case_for(who)


@app.post("/keys")
def keys(k: Keys) -> dict:
    """The box in the interface. In memory only; never echoed back, never written."""
    _KEYS["twilio_account_sid"] = k.twilio_account_sid.strip()
    _KEYS["twilio_auth_token"] = k.twilio_auth_token.strip()
    return {"status": "alive", "message": "keys held in memory for this run",
            "twilio_seated": bool(_KEYS["twilio_account_sid"] and _KEYS["twilio_auth_token"])}


@app.post("/check/phone")
def phone(n: Number) -> dict:
    return check_phone(n.number, _KEYS["twilio_account_sid"], _KEYS["twilio_auth_token"])


@app.post("/check/mail")
def mail(a: Address) -> dict:
    return check_mail(a.address)


if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host=HOST, port=PORT)
