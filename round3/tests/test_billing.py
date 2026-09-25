"""
Run:
    pip install pytest
    python -m pytest tests/ -q

Or without pytest (prints a pass/fail summary, does not stop at the first
failure):
    python tests/test_billing.py

Four of these tests fail on a clean checkout. They are the bug reports from
finance and support, written as tests. Three pass. Whether the three that pass
are worth anything is for you to judge.
"""

import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Coupon, Plan, Subscription
from repository import Repository
from service import BillingService, PaymentDeclined
import pricing


class FakeGateway:
    def __init__(self, fail_for=()):
        self.fail_for = set(fail_for)
        self.calls = []

    def charge(self, customer_id, amount):
        self.calls.append((customer_id, amount))
        if customer_id in self.fail_for:
            raise PaymentDeclined(customer_id)
        return True


PLAN = Plan("pro", "Pro", 10_000)          # NGN 100.00


def make(sub_overrides=None, gateway=None):
    sub = Subscription("s1", "cust1", PLAN, date(2026, 6, 1))
    for k, v in (sub_overrides or {}).items():
        setattr(sub, k, v)
    repo = Repository([sub])
    return sub, repo, BillingService(repo, gateway or FakeGateway())


# --- failing: reported by finance ------------------------------------------

def test_full_month_when_started_on_the_first():
    """A plan started on the 1st should be charged for the whole month."""
    assert pricing.prorated_amount(PLAN, date(2026, 6, 1)) == 10_000


def test_discount_applies_before_tax():
    """10% off NGN 100.00 -> 90.00 subtotal, VAT 7.5% -> total 96.75."""
    sub, repo, svc = make({"coupon": Coupon("SAVE10", 10)})
    invoice = svc.invoice_for(sub)
    assert invoice.discount == 1_000
    assert invoice.tax == 675
    assert invoice.total == 9_675


# --- failing: reported by support ------------------------------------------

def test_cancelled_subscription_is_not_billed():
    sub, repo, svc = make({"status": "cancelled"})
    assert repo.find_billable() == []


def test_retry_does_not_charge_twice():
    sub, repo, svc = make()
    svc.charge(sub, idempotency_key="k1")
    svc.charge(sub, idempotency_key="k1")      # job runner retried
    assert len(svc.gateway.calls) == 1
    assert len(repo.charges) == 1


# --- passing ---------------------------------------------------------------

def test_charge_succeeds():
    sub, repo, svc = make()
    charge = svc.charge(sub, idempotency_key="k2")
    assert charge.status == "succeeded"


def test_declined_payment_marks_past_due():
    sub, repo, svc = make(gateway=FakeGateway(fail_for=["cust1"]))
    svc.charge(sub, idempotency_key="k3")
    assert sub.status == "past_due"


def test_run_cycle_returns_charges():
    sub, repo, svc = make()
    assert svc.run_cycle()


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print("PASS", t.__name__)
        except AssertionError as e:
            failed += 1
            print("FAIL", t.__name__, "-", e or "assertion failed")
        except Exception as e:
            failed += 1
            print("ERROR", t.__name__, "-", type(e).__name__, e)
    print(f"\n{len(tests) - failed} passed, {failed} failed")