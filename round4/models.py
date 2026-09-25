"""Domain objects for the quote cache.

Prices are in minor units. Timestamps are float seconds from a Clock.
"""

from dataclasses import dataclass


@dataclass
class Quote:
    symbol: str
    bid: int
    ask: int
    as_of: float

    @property
    def mid(self):
        return (self.bid + self.ask) // 2


@dataclass
class Entry:
    """One cached value plus the time it was stored."""
    value: object
    stored_at: float
    error: bool = False


class Clock:
    """Injectable clock so tests don't sleep. Production passes the real one."""

    def __init__(self, now=0.0):
        self._now = now

    def now(self):
        return self._now

    def advance(self, seconds):
        self._now += seconds
        return self._now