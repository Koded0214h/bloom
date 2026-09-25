"""Domain objects for the settlement service."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Account:
    account_id: str
    currency: str
    # Credit limit: how far below zero this account may go. 0 = no overdraft.
    overdraft_limit: int = 0


@dataclass
class Entry:
    """A single side of a double-entry posting. Amounts are in minor units (kobo/cents)."""
    entry_id: int
    transfer_id: str
    account_id: str
    amount: int          # positive = credit into the account, negative = debit
    kind: str            # "transfer" | "fee" | "reversal"


@dataclass
class Transfer:
    transfer_id: str
    source_id: str
    dest_id: str
    amount: int
    fee: int = 0
    reversed: bool = False
    entries: List[Entry] = field(default_factory=list)