"""
Run:
    python tests/test_cache.py           # full summary, no early exit
    python -m pytest tests/ -q           # after: pip install pytest

Five of these fail on a clean checkout. They are the incident reports, written
as tests. Three pass.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from feed import FakeFeed
from lru import LRUStore
from models import Clock
from service import QuoteService, UnknownSymbol


def make(capacity=128, ttl=5.0, stale_ttl=30.0, **feed_kwargs):
    clock = Clock(1000.0)
    feed = FakeFeed(clock, **feed_kwargs)
    svc = QuoteService(feed, clock, capacity=capacity, ttl=ttl, stale_ttl=stale_ttl)
    return clock, feed, svc


# --- failing: reported by the trading desk --------------------------------

def test_recently_read_key_is_not_evicted():
    """A key read just now must outlive a key nobody has touched."""
    store = LRUStore(capacity=2)
    store.put("a", 1)
    store.put("b", 2)
    store.get("a")            # 'a' is now the most recently used
    store.put("c", 3)         # should evict 'b'
    assert store.get("a") == 1
    assert store.get("b") is None
    assert store.get("c") == 3


def test_dead_entry_is_never_served():
    """Past ttl + stale_ttl the cache must go back to upstream."""
    clock, feed, svc = make(ttl=5.0, stale_ttl=10.0)
    first = svc.get("BLM")
    clock.advance(100.0)          # well past ttl + stale_ttl: this entry is dead
    second = svc.get("BLM")
    assert second.as_of == clock.now(), "a dead entry was served to the caller"
    assert second is not first


def test_case_insensitive_symbols_share_one_entry():
    clock, feed, svc = make()
    svc.get("BLM")
    svc.get("blm")
    assert feed.call_count() == 1


# --- failing: reported by the platform team -------------------------------

def test_upstream_error_is_not_cached():
    clock, feed, svc = make(fail_for=["BLM"])
    try:
        svc.get("BLM")
    except Exception:
        pass
    feed.fail_for.clear()
    quote = svc.get("BLM")
    assert quote is not None
    assert quote.symbol == "BLM"


def test_duplicate_symbols_hit_upstream_once():
    clock, feed, svc = make()
    svc.get_many(["BLM", "blm", "BLM"])
    assert feed.call_count("BLM") == 1


# --- passing --------------------------------------------------------------

def test_second_read_is_a_cache_hit():
    clock, feed, svc = make()
    svc.get("BLM")
    svc.get("BLM")
    assert feed.call_count("BLM") == 1


def test_unknown_symbol_raises():
    clock, feed, svc = make()
    try:
        svc.get("NOPE")
        raised = False
    except UnknownSymbol:
        raised = True
    assert raised


def test_spread_is_positive():
    clock, feed, svc = make()
    assert svc.spread("BLM") > 0


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print("PASS ", t.__name__)
        except AssertionError as e:
            failed += 1
            print("FAIL ", t.__name__, "-", e or "assertion failed")
        except Exception as e:
            failed += 1
            print("ERROR", t.__name__, "-", type(e).__name__, e)
    print(f"\n{len(tests) - failed} passed, {failed} failed")