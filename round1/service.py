"""
Public service API.

Requirements from the payments team:
  1. transfer() moves `amount` from source to dest, and charges the sender a fee.
  2. Callers retry on network failure, so transfer() must be idempotent:
     the same idempotency_key must never move money twice.
  3. A transfer must be rejected if the sender cannot cover amount + fee.
  4. Source and destination must be the same currency.
  5. refund() reverses a completed transfer exactly once.
  6. Multiple worker threads call this service concurrently.
"""

import uuid

import fees
from ledger import InsufficientFunds, Ledger


class SettlementService:
    def __init__(self, accounts):
        self.ledger = Ledger(accounts)
        self.transfers = {}
        self.seen_keys = {}

    def transfer(self, source_id, dest_id, amount, idempotency_key):
        if amount <= 0:
            raise ValueError("amount must be positive")

        fee = fees.fee_for(amount)
        total = amount + fee

        if not self.ledger.can_debit(source_id, total):
            raise InsufficientFunds(source_id)

        transfer_id = str(uuid.uuid4())

        with self.ledger.lock:
            self.ledger.post(transfer_id, source_id, -amount)
            self.ledger.post(transfer_id, dest_id, amount)
            self.ledger.post(transfer_id, dest_id, -fee, kind="fee")

        self.transfers[transfer_id] = {
            "source": source_id,
            "dest": dest_id,
            "amount": amount,
            "fee": fee,
            "reversed": False,
        }

        if idempotency_key in self.seen_keys:
            return self.seen_keys[idempotency_key]
        else: 
            self.seen_keys[idempotency_key] = transfer_id

        return transfer_id

    def refund(self, transfer_id):
        record = self.transfers.get(transfer_id)
        if record is None:
            raise KeyError(transfer_id)

        with self.ledger.lock:
            self.ledger.reverse(transfer_id)

        record["reversed"] = True
        return True

    def balance(self, account_id):
        return self.ledger.balance(account_id)