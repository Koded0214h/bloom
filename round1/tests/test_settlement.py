"""Run with:  cd settlement && python -m pytest tests/ -q   (or: python tests/test_settlement.py)"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Account
from service import SettlementService


def make_service():
    accounts = [
        Account("alice", "NGN"),
        Account("bob", "NGN"),
        Account("float", "NGN", overdraft_limit=10_000_000),
    ]
    svc = SettlementService(accounts)
    # fund alice from the float account
    with svc.ledger.lock:
        svc.ledger.post("seed", "float", -1_000_000)
        svc.ledger.post("seed", "alice", 1_000_000)
    return svc


def test_transfer_returns_id():
    svc = make_service()
    tid = svc.transfer("alice", "bob", 10_000, idempotency_key="k1")
    assert tid is not None


def test_transfer_moves_money():
    svc = make_service()
    svc.transfer("alice", "bob", 10_000, idempotency_key="k2")
    assert svc.balance("bob") > 0


def test_fee_is_charged():
    svc = make_service()
    svc.transfer("alice", "bob", 10_000, idempotency_key="k3")
    fee_entries = [e for e in svc.ledger.entries if e.kind == "fee"]
    assert len(fee_entries) == 1


if __name__ == "__main__":
    test_transfer_returns_id()
    test_transfer_moves_money()
    test_fee_is_charged()
    print("all tests passed")