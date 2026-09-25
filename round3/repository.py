"""In-memory repository layer.

Contract:
  * find_billable() returns subscriptions that should be charged this cycle:
    status "active" or "past_due". Cancelled subscriptions are never billable.
    A subscription flagged cancel_at_period_end is still billable until the
    cycle it was cancelled in has ended, i.e. it is billable while its status
    is still active.
  * save_charge() is called from multiple worker threads.
"""

import threading


class Repository:
    def __init__(self, subscriptions=None):
        self.subscriptions = list(subscriptions or [])
        self.charges = {}
        self.lock = threading.Lock()

    def find_billable(self):
        result = []
        for s in self.subscriptions:
            if s.status == "active" or s.status == "past_due" or not s.cancel_at_period_end: 
                result.append(s)
        return result

    def get(self, subscription_id):
        for s in self.subscriptions:
            if s.subscription_id == subscription_id:
                return s
        return None

    def save_charge(self, charge):
        self.charges[charge.charge_id] = charge
        return charge

    def charge_by_key(self, idempotency_key):
        for c in self.charges.values():
            if c.idempotency_key == idempotency_key:
                return c
        return None

    def cancel(self, subscription_id):
        for s in self.subscriptions:
            if s.subscription_id == subscription_id:
                s.status = "cancelled"
                self.subscriptions.remove(s)
                return True
        return False