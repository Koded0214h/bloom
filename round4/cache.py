"""TTL cache with stale-while-revalidate.

Contract:
  * An entry is FRESH for `ttl` seconds after it was stored. At exactly ttl
    seconds old it is no longer fresh.
  * An entry between ttl and ttl + stale_ttl old is STALE: it may be served to
    the caller, but a refresh must be triggered.
  * An entry older than ttl + stale_ttl is DEAD and must never be served.
  * Single flight: while a refresh for a key is already running, other callers
    must not trigger a second upstream call for that same key.
  * Errors from upstream are never cached. A failed load must be retried on the
    next call.
  * stats() reports hits (served from cache, fresh or stale) and misses
    (had to wait on upstream).
"""

import threading

from lru import LRUStore
from models import Entry


class QuoteCache:
    def __init__(self, loader, clock, capacity=128, ttl=5.0, stale_ttl=30.0):
        self.loader = loader
        self.clock = clock
        self.store = LRUStore(capacity)
        self.ttl = ttl
        self.stale_ttl = stale_ttl
        self.in_flight = set()
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    def _age(self, entry):
        return self.clock.now() - entry.stored_at

    def is_fresh(self, entry):
        return self._age(entry) <= self.ttl

    def is_stale(self, entry):
        age = self._age(entry)
        return age > self.ttl

    def get(self, key):
        entry = self.store.get(key)

        if entry is not None and self.is_fresh(entry):
            self.hits += 1
            return entry.value

        if entry is not None and self.is_stale(entry):
            self.hits += 1
            self._refresh(key)
            return entry.value

        self.misses += 1
        return self._load(key)

    def _refresh(self, key):
        if key in self.in_flight:
            return
        self.in_flight.add(key)
        try:
            self._load(key)
        finally:
            self.in_flight.discard(key)

    def _load(self, key):
        try:
            value = self.loader(key)
        except Exception:
            self.store.put(key, Entry(value=None, stored_at=self.clock.now(), error=True))
            return None
        self.store.put(key, Entry(value=value, stored_at=self.clock.now()))
        return value

    def invalidate(self, key):
        return self.store.delete(key)

    def stats(self):
        return {"hits": self.hits, "misses": self.misses, "size": len(self.store)}