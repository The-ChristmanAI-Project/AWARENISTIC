# AWARENISTIC — Aware for you.

## Why This Being Exists

A sixty-two-year-old woman sits at home. She is lonely. A forty-one-year-old retired Army man writes to her every day. He loves her. He cannot video call, for security reasons. He is deployed. He needs eight hundred dollars in gift cards for his leave papers so he can come home to her, and she should not tell her daughter, because her daughter would not understand.

He was never born. Thousands of people are read that exact script every day, and the only thing the world has to offer them is a pamphlet, written for a person who is not currently on the phone with him.

Everett Christman watched a news report about this in September 2026 and could not sit still through it. Nobody was touching it from the target's side. So this being was built, in one day, out of the scam section of HONESTY, and it is free, and it stays free, so these people get stopped.

## Who This Being Serves

Seniors first. Men and women both. The lonely widow. The grandfather who gets the call that his grandson is in jail. The retiree whose computer "has a virus." The man told the IRS has a warrant. Anyone at home being worked by a person who does not exist.

## What This Being Promises

I will tell you the truth about who is talking to you, the moment I can see it, and I will never let you find out from your bank.

---

## What It Does

It reads what strangers send, keeps each stranger's messages together, and reads the whole thread against the scam book: thirteen moves, from asked-for-money to you've-won-something. The rule, stated once: one move is a flag; three moves is a case; money plus any other move is a case; a story move (government, relative in trouble, tech support, windfall) plus any other move is a case; leave papers or being asked to receive or forward money is a case alone.

When it fires, it speaks to the person, not the owner of the machine and never the stranger, in three parts: what it saw, in the stranger's own words; what it means, quoting what the Army, the IRS, Microsoft, and the courts say about themselves; what to do now. Do not send anything. Do not tell them you checked. Show this to someone you trust. Report it.

Two real checks run on request: the phone number through Twilio Lookup (only with a key the person entered, in the interface, held in memory), and the mail address through public DNS and the domain registry (no key).

What it will not do: speak to the scammer; claim to verify anyone's military service; send anything anywhere without the person's own hand on it; run a paid check on anyone's key but the person's own.

## Architecture

```
AWARENISTIC/
├── IDENTITY.md       — Who this being is. Written first. Law for every file below.
├── SOUL.py           — Non-negotiables and prohibitions. Written second.
├── CARDINAL_RULES.md — Everett Christman's Cardinal Rules of Code, all 15.
├── SAFETY.py         — The scam book: thirteen moves, the rule, crisis path, output gate.
├── VOICE.py          — The three-part card, in the person's words.
├── MEMORY.py         — The stranger's thread, on the person's own device, in a plain file.
├── CHECKS.py         — Phone (Twilio, person's key) and mail (DNS + registry, no key).
├── CORE.py           — One message in, the whole thread read, the card out.
├── API.py            — The local door on 127.0.0.1:3600.
├── .env.example      — Documents the two optional variables. No .env is used in this house.
├── .gitignore
├── requirements.txt  — Pinned to what was actually installed.
└── tests/            — test_soul, test_safety, test_memory, test_core, plus conftest.
```

## Getting Started

### Prerequisites

- Python 3.10 or newer. Built and tested on 3.12.

### Installation

```bash
git clone https://github.com/The-ChristmanAI-Project/AWARENISTIC
cd AWARENISTIC
pip install -r requirements.txt
```

No dot env to fill in. Keys go in through the interface (POST /keys) and live in memory for the run.

### Running

```bash
python3 API.py
```

Listens on 127.0.0.1 port 3600. It does not bind to 0.0.0.0 and never will. Tested.

### Health Check

```bash
curl http://127.0.0.1:3600/health
# {"status":"alive","being":"Awarenistic"}
```

### The Door

| Method | Path | What it does |
|---|---|---|
| GET | /health | Alive check |
| GET | /identity | Name, version, purpose, promise, population |
| POST | /message | `{"text": "...", "who": "James"}` — reads one message, returns status, level, and the card |
| GET | /case/{who} | The standing case for one stranger from everything they have sent |
| POST | /keys | `{"twilio_account_sid": "...", "twilio_auth_token": "..."}` — held in memory only |
| POST | /check/phone | `{"number": "..."}` — line type, carrier, country; "not checked" without a key |
| POST | /check/mail | `{"address": "..."}` — free-mail, takes mail, SPF, domain age |

### Tests

```bash
pytest tests/
# 37 tests. Safety first. All four files must pass before this being is considered alive.
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| AWARENISTIC_PORT | No | Port for the local door. Default 3600. Always bound to 127.0.0.1. |
| AWARENISTIC_LEDGER | No | Path of the person's own record file. Default `awarenistic-ledger.jsonl` beside the being. |

Twilio credentials are not environment variables. They are entered through POST /keys and are never written to disk.

## Where It Was Born

Awarenistic began as a section inside HONESTY (github.com/The-ChristmanAI-Project/HONESTY, `src/lib/scam.ts`) on the morning of 30 September 2026 and was named and given a house of its own the same afternoon. HONESTY remains its ledger: cases it catches are meant to be written there so they count.

## Not Built Yet, Said Plainly

- Reading messages straight off a phone's mail, SMS, or call log. Today the interface hands messages to the door; the phone-side reader is the next organ.
- Photo check, so a stolen soldier's face gets caught. No reverse-image service has been chosen.
- Voice. The calls are where the pressure happens; the Filament already hears, and is not yet wired here.
- The trusted-contact alarm. Today the card says show this to someone you trust; the silent alarm to a named person, the way Sierra does it, is not built.

## Cardinal Rules Compliance

This being operates under Everett Christman's Cardinal Rules of Code. All 15 apply. Rule 13 is gospel. There is no fabricated functionality in this build; everything above that says it works was run.

*How can we help you love yourself more?*
