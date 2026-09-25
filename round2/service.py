"""
Public service API.

Requirements from the trading desk:
  1. submit() registers a client order.
  2. on_fill() takes an execution from the exchange, splits it across open
     orders for that symbol, and updates each client's position.
  3. The exchange sometimes redelivers the same fill_id. A fill must never be
     applied twice.
  4. cancel() removes an order from future allocations. Shares already
     allocated to it stay allocated.
  5. A fill for a symbol nobody wants must not be silently lost — raise.
  6. Several exchange-feed threads call on_fill() concurrently.
"""

import threading

import allocation
from positions import PositionBook


class NoOpenOrders(Exception):
    pass


class AllocationService:
    def __init__(self):
        self.orders = []
        self.book = PositionBook()
        self.applied_fills = set()
        self.lock = threading.Lock()

    def submit(self, order):
        self.orders.append(order)
        return order.order_id

    def cancel(self, order_id):
        for o in self.orders:
            if o.order_id == order_id:
                o.cancelled = True
                self.orders.remove(o)
                return True
        return False

    def on_fill(self, fill):
        # since they call fill concurrently, itll need to acquire lock at some point
        
        allocations = allocation.allocate(self.orders, fill)
        if not allocations:
            raise NoOpenOrders(fill.symbol)

        if fill.fill_id in self.applied_fills:
            return {}

        for order_id, qty in allocations.items():
            order = self._find(order_id)
            order.filled += qty
            self.book.apply(order.client_id, order.symbol, qty, fill.price)

        self.applied_fills.add(fill.fill_id)
        return allocations

    def _find(self, order_id):
        for o in self.orders:
            if o.order_id == order_id:
                return o
        return None

    def position(self, client_id, symbol):
        return self.book.get(client_id, symbol)