"""
Quote service — what the trading UI and the pricing jobs call.

Requirements:
  1. get(symbol) returns the latest quote, from cache when possible.
  2. get_many(symbols) returns a dict for every symbol asked for, and must
     call upstream at most once per distinct symbol.
  3. Symbols are case-insensitive: "blm" and "BLM" are the same instrument and
     must share one cache entry.
  4. warm(symbols) preloads the cache before market open.
  5. spread(symbol) returns ask - bid in minor units.
  6. A symbol the feed does not know raises UnknownSymbol, and that failure is
     not cached.
  7. The UI and the jobs call this service from different threads.
"""

from cache import QuoteCache


class UnknownSymbol(Exception):
    pass


class QuoteService:
    def __init__(self, feed, clock, **cache_kwargs):
        self.feed = feed
        self.cache = QuoteCache(self._load, clock, **cache_kwargs)

    def _load(self, symbol):
        quote = self.feed.fetch(symbol.upper())
        if quote is None:
            raise UnknownSymbol(symbol)
        return quote

    def get(self, symbol):
        quote = self.cache.get(symbol)
        if quote is None:
            raise UnknownSymbol(symbol)
        return quote

    def get_many(self, symbols):
        out = {}
        for s in symbols:
            out[s] = self.get(s)
        return out

    def warm(self, symbols):
        for s in symbols:
            try:
                self.get(s)
            except UnknownSymbol:
                pass
        return len(self.cache.store)

    def spread(self, symbol):
        quote = self.get(symbol)
        return quote.ask - quote.bid

    def stats(self):
        return self.cache.stats()