"""Fake upstream market data feed. Counts calls so tests can assert on them."""

from models import Quote


class FakeFeed:
    def __init__(self, clock, prices=None, fail_for=()):
        self.clock = clock
        self.prices = dict(prices or {"BLM": (9_990, 10_010), "ACME": (4_400, 4_450)})
        self.fail_for = set(fail_for)
        self.calls = []

    def fetch(self, symbol):
        self.calls.append(symbol)
        if symbol in self.fail_for:
            raise ConnectionError(symbol)
        if symbol not in self.prices:
            return None
        bid, ask = self.prices[symbol]
        return Quote(symbol=symbol, bid=bid, ask=ask, as_of=self.clock.now())

    def call_count(self, symbol=None):
        if symbol is None:
            return len(self.calls)
        return sum(1 for c in self.calls if c == symbol)