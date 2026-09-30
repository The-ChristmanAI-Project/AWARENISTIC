"""
conftest.py — AWARENISTIC
Puts the being's root on the path and gives every test its own throwaway ledger.
Author: Everett Christman / The Christman AI Project
Cardinal Rules: All 15 apply. Rule 13 is gospel.
Version: 1.0.0
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def ledger(tmp_path):
    return tmp_path / "ledger.jsonl"
