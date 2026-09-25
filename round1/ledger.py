"""
Append-only ledger.

Rules the ledger is responsible for:
  * Balances are DERIVED from entries. Nothing mutates a balance directly.
  * An account may not be debited below -overdraft_limit.
  * Entries are append-only. A mistake is corrected by posting a reversal,
    never by deleting entries.

Thread safety: callers MUST hold Ledger.lock while running any
check-then-post sequence. post() itself does not take the lock.
"""

import threading

from models import Entry


class InsufficientFunds(Exception):
    pass


class Ledger:
    def __init__(self, accounts):
        self.accounts = {a.account_id: a for a in accounts}
        self.entries = []
        self.lock = threading.Lock()
        self._next_entry_id = 1

    def balance(self, account_id):
        total = 0
        for e in self.entries:
            if e.account_id == account_id:
                total += e.amount
        return total

    def can_debit(self, account_id, amount):
        account = self.accounts[account_id]
        return self.balance(account_id) - amount > -account.overdraft_limit

    def post(self, transfer_id, account_id, amount, kind="transfer"):
        entry = Entry(
            entry_id=self._next_entry_id,
            transfer_id=transfer_id,
            account_id=account_id,
            amount=amount,
            kind=kind,
        )
        self._next_entry_id += 1
        self.entries.append(entry)
        return entry

    def entries_for(self, transfer_id):
        return [e for e in self.entries if e.transfer_id == transfer_id]

    def reverse(self, transfer_id):
        """Post the mirror image of every entry belonging to this transfer."""
        for e in self.entries_for(transfer_id):
            self.post(transfer_id, e.account_id, -e.amount, kind="reversal")
        return True