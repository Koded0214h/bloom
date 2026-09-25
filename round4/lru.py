"""Bounded LRU store.

Contract:
  * Holds at most `capacity` items.
  * When a new key is inserted into a full store, the LEAST recently used key
    is evicted. Nothing else is ever evicted.
  * Both get() and put() count as "using" a key — a key that was just read is
    the most recently used, and must not be the next one evicted.
  * keys() returns keys from least to most recently used.
"""

from collections import OrderedDict


class LRUStore:
    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self._data = OrderedDict()
        self.evictions = 0

    def get(self, key):
        if key not in self._data:
            return None
        return self._data[key]

    def put(self, key, value):
        self._data[key] = value
        self._data.move_to_end(key)
        if len(self._data) > self.capacity:
            self._data.popitem(last=True)
            self.evictions += 1

    def delete(self, key):
        if key in self._data:
            del self._data[key]
            return True
        return False

    def keys(self):
        return list(self._data.keys())

    def __len__(self):
        return len(self._data)